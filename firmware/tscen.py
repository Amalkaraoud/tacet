"""TACET - scenarios de demonstration reproductibles.

Operateur *simule* : les intervalles de frappe sont generes par un LCG entier
deterministe, identique sur PC et sur ESP32, de sorte que la sortie Wokwi peut
etre comparee a la reference hote. Ce n'est PAS un humain : voir docs.
"""
import tproto as P
import tbio as B
import tconfig as cfg


class Rng:
    def __init__(self, seed=20261116):
        self.s = seed & 0xFFFFFFFF

    def u(self, n):                       # entier uniforme 0..n-1
        self.s = (self.s * 1664525 + 1013904223) & 0xFFFFFFFF
        return (self.s >> 8) % n

    def gauss_milli(self):                # ~N(0,1) x 1000, somme de 12 uniformes
        return sum([self.u(1001) for _ in range(12)]) - 6000


def typing(rng, mu, cv_milli, n=cfg.PIN_LEN + 1):
    """Horodatages (ms) de n touches : intervalle = mu * (1 + cv*g)."""
    ts = [0]
    for _ in range(n - 1):
        d = mu + (mu * cv_milli * rng.gauss_milli()) // 1000000
        ts.append(ts[-1] + max(40, d))
    return ts


MU = {1: 220, 2: 260}
CV = 180


class Ctx:
    def __init__(self, link, term, c2, seed=1):
        self.link, self.term, self.c2 = link, term, c2
        self.rng = Rng(seed)
        self.prof = {}
        for op in (1, 2):
            self.prof[op] = B.Profile().enrol(
                [typing(self.rng, MU[op], CV) for _ in range(8)])
        self.cmd = 100
        self.last_frame = None
        self.executed = []


NAMES = ["S1 nominal 2 op.", "S2 PIN contrainte",
         "S3 stress rythme", "S4 rejeu adverse",
         "S5 trame alteree", "S6 force brute PIN"]


def _send(ctx, op, pin, mu, par, cv=CV):
    ts = typing(ctx.rng, mu, cv)
    bio = ctx.prof[op].score(ts)
    ctx.term.submit(op, pin, ctx.cmd, 1, par, bio)
    return bio


def _flush(ctx, out, log):
    """Emet des creneaux jusqu'a vidage de la file + 1 creneau de couverture."""
    n = 0
    while ctx.term.pending() or n == 0:
        f, ev = ctx.link.slot()
        ctx.last_frame = f
        n += 1
        if ev and ev["kind"] != "COVER":
            out.append(ev["kind"])
            log(ev)
    f, ev = ctx.link.slot()
    ctx.last_frame = f


def run(i, ctx, log):
    """Execute le scenario i (0..5). Retourne la liste des verdicts C2."""
    out = []
    ctx.cmd += 1
    pn1, pd1 = cfg.OPERATORS[1]
    pn2, pd2 = cfg.OPERATORS[2]
    if i == 0:
        _send(ctx, 1, pn1, MU[1], 250000)
        _send(ctx, 2, pn2, MU[2], 250000)
    elif i == 1:
        _send(ctx, 1, pn1, MU[1], 250000)
        _send(ctx, 2, pd2, MU[2], 250000)
    elif i == 2:
        _send(ctx, 1, pn1, 120, 250000, cv=320)      # frappe precipitee/saccadee
        _send(ctx, 2, pn2, MU[2], 250000)
    elif i == 3:
        _flush(ctx, [], lambda e: None)
        ctx.link.slot(inject=ctx.last_frame)           # rejeu du dernier cadre
        e = ctx.c2.log[-1]
        out.append(e["kind"]); log(e)
        return out
    elif i == 4:
        _send(ctx, 1, pn1, MU[1], 5)
        _flush(ctx, [], lambda e: None)
        from tchannel import tamper
        ctx.link.slot(inject=tamper(ctx.last_frame))
        e = ctx.c2.log[-1]
        out.append(e["kind"]); log(e)
        return out
    elif i == 5:
        for _ in range(3):
            ctx.term.submit(1, "000000", ctx.cmd, 1, 1, 0)
        _flush(ctx, out, log)
        ctx.term.submit(1, pn1, ctx.cmd, 1, 1, 0)
        _flush(ctx, out, log)
        return out
    _flush(ctx, out, log)
    return out
