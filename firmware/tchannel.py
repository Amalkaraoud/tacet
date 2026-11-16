"""TACET - modele de liaison (PAS une simulation radio physique).

Modelise : debit constant (1 trame / creneau), perte aleatoire, et un
observateur passif qui n'enregistre que ce qu'un ecouteur voit (instant, taille).
Les actions d'un adversaire actif (rejeu, alteration) sont des fonctions pures.
"""


class Observer:
    def __init__(self):
        self.seen = []      # (t_ms, taille)

    def tap(self, t, frame):
        self.seen.append((t, len(frame)))

    def summary(self):
        sizes = set([s for _, s in self.seen])
        gaps = set([self.seen[i + 1][0] - self.seen[i][0]
                    for i in range(len(self.seen) - 1)])
        return {"n": len(self.seen), "sizes": sorted(sizes), "gaps": sorted(gaps)}


def replay(frame):
    return bytes(frame)


def tamper(frame, bit=100):
    b = bytearray(frame)
    b[bit // 8] ^= 1 << (bit % 8)
    return bytes(b)


class Link:
    """Terminal -> canal -> C2, un creneau a la fois."""

    def __init__(self, terminal, c2, observer, slot_ms=1000, loss=0.0, rnd=None):
        self.t = terminal
        self.c2 = c2
        self.obs = observer
        self.slot_ms = slot_ms
        self.loss = loss
        self.rnd = rnd
        self.now = 0

    def slot(self, inject=None):
        """Emet exactement une trame ; `inject` = trame adverse supplementaire."""
        f = self.t.next_frame()
        self.now += self.slot_ms
        self.obs.tap(self.now, f)
        ev = None
        if not (self.rnd and self.rnd() < self.loss):
            ev = self.c2.receive(f)
        if inject is not None:
            ev = self.c2.receive(inject)
        return f, ev
