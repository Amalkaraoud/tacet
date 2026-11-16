"""TACET - protocole d'autorisation sous contrainte.

Trame fixe de 64 octets : ctr(4) | chiffre(48) | tag_lien(12).
Toutes les trames (ordre reel ou couverture) ont la meme taille, partent a debit
constant et sont indiscernables de l'exterieur. Le terminal ne verifie JAMAIS le
PIN et ne connait pas le PIN de contrainte : la semantique "contrainte" n'existe
que cote C2.

Clair (48 o) : type1 | op1 | cmd2 | action1 | param4 | bio1 | tag_op16 | pad22
"""
from tcrypto import (hmac_sha256, ct_equal, xor_bytes, keystream, u32, derive,
                     urandom)

FRAME_LEN = 64
PT_LEN = 48
LTAG_LEN = 12
OTAG_LEN = 16
T_COVER = 0
T_AUTH = 1


class Keys:
    def __init__(self, master):
        self.kenc = derive(master, b"TACET-ENC")
        self.kmac = derive(master, b"TACET-MAC")


def op_key(kmac, op_id, pin):
    return hmac_sha256(kmac, b"OP" + bytes([op_id]) + pin.encode())


def _otag(kop, ctr, body):
    return hmac_sha256(kop, u32(ctr) + body)[:OTAG_LEN]


class Terminal:
    """Cote operateur. N'a aucune connaissance des PIN valides."""

    def __init__(self, keys, rand=None):
        self.k = keys
        self.ctr = 0
        self.q = []
        self.rand = rand or urandom

    def submit(self, op_id, pin, cmd_id, action, param, bio=0):
        self.q.append((op_id, pin, cmd_id, action, param, bio))

    def pending(self):
        return len(self.q)

    def next_frame(self):
        """Appele a chaque creneau : exactement une trame de 64 o."""
        self.ctr += 1
        ctr = self.ctr
        if self.q:
            op, pin, cmd, act, par, bio = self.q.pop(0)
            body = (bytes([T_AUTH, op]) + bytes([cmd >> 8, cmd & 255, act])
                    + u32(par) + bytes([bio & 255]))
            tag_op = _otag(op_key(self.k.kmac, op, pin), ctr, body)
            pt = body + tag_op + self.rand(PT_LEN - len(body) - OTAG_LEN)
        else:
            pt = bytes([T_COVER]) + self.rand(PT_LEN - 1)
        ct = xor_bytes(pt, keystream(self.k.kenc, ctr, PT_LEN))
        tag = hmac_sha256(self.k.kmac, u32(ctr) + ct)[:LTAG_LEN]
        return u32(ctr) + ct + tag


class C2:
    """Centre de commandement / banque : seul detenteur des PIN et des seuils."""

    def __init__(self, keys, operators, bio_thr=96, max_fail=3, window=8,
                 on_execute=None):
        self.k = keys
        self.ops = operators          # op_id -> (pin_normal, pin_contrainte)
        self.bio_thr = bio_thr
        self.max_fail = max_fail
        self.window = window
        self.on_execute = on_execute
        self.last = 0
        self.fails = {}
        self.locked = set()
        self.cmds = {}                # cmd -> {"first":ctr,"ok":set,"bad":kind}
        self.log = []

    def _ev(self, kind, ctr, **kw):
        e = {"kind": kind, "ctr": ctr}
        e.update(kw)
        self.log.append(e)
        return e

    def receive(self, frame):
        if len(frame) != FRAME_LEN:
            return self._ev("DROP_FORMAT", -1)
        ctr = int.from_bytes(frame[:4], "big")
        ct = frame[4:52]
        tag = frame[52:]
        exp = hmac_sha256(self.k.kmac, frame[:4] + ct)[:LTAG_LEN]
        if not ct_equal(tag, exp):
            return self._ev("DROP_TAMPER", ctr)
        if ctr <= self.last:
            return self._ev("DROP_REPLAY", ctr)
        self.last = ctr
        pt = xor_bytes(ct, keystream(self.k.kenc, ctr, PT_LEN))
        if pt[0] == T_COVER:
            return self._ev("COVER", ctr)
        if pt[0] != T_AUTH:
            return self._ev("DROP_FORMAT", ctr)
        op = pt[1]
        cmd = (pt[2] << 8) | pt[3]
        act = pt[4]
        par = int.from_bytes(pt[5:9], "big")
        bio = pt[9]
        body = pt[:10]
        otag = pt[10:10 + OTAG_LEN]
        if op not in self.ops:
            return self._ev("FAIL", ctr, op=op, cmd=cmd)
        if op in self.locked:
            return self._ev("LOCKED", ctr, op=op, cmd=cmd)
        pn, pd = self.ops[op]
        status = None
        for name, pin in (("OK", pn), ("DURESS", pd)):
            exp_o = _otag(op_key(self.k.kmac, op, pin), ctr, body[:10])
            if ct_equal(otag, exp_o):
                status = name
                break
        if status is None:
            n = self.fails.get(op, 0) + 1
            self.fails[op] = n
            if n >= self.max_fail:
                self.locked.add(op)
            return self._ev("FAIL", ctr, op=op, cmd=cmd, fails=n,
                            locked=op in self.locked)
        self.fails[op] = 0
        if status == "OK" and bio >= self.bio_thr:
            status = "SUSPECT"
        c = self.cmds.get(cmd)
        if c is None or ctr - c["first"] > self.window:
            c = {"first": ctr, "ok": set(), "bad": None}
            self.cmds[cmd] = c
        if status in ("DURESS", "SUSPECT"):
            c["bad"] = status
        if c["bad"]:
            kind = "DECOY" if c["bad"] == "DURESS" else "HOLD"
            return self._ev(kind, ctr, op=op, cmd=cmd, par=par, bio=bio,
                            silent=True)
        c["ok"].add(op)
        if len(c["ok"]) >= 2:
            c["bad"] = "DONE"
            if self.on_execute:
                self.on_execute(cmd, act, par)
            return self._ev("EXECUTE", ctr, cmd=cmd, par=par, ops=sorted(c["ok"]))
        return self._ev("PENDING", ctr, op=op, cmd=cmd, bio=bio)

    def ack(self, ctr, rand=None):
        """Acquittement descendant : meme forme quelle que soit l'issue."""
        r = rand or urandom
        pt = bytes([0xA5]) + u32(ctr) + r(PT_LEN - 5)
        ct = xor_bytes(pt, keystream(self.k.kenc, ctr, PT_LEN, b"D"))
        return u32(ctr) + ct + hmac_sha256(self.k.kmac, b"D" + u32(ctr) + ct)[:LTAG_LEN]
