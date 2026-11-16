"""TACET - signal comportemental implicite : rythme de frappe du PIN.

Profil robuste simple (moyenne et coefficient de variation des intervalles
inter-touches), appris a l'enrolement. Score 0..255 = 32 x ecart maximal en
ecarts-types ; le seuil C2 (96) correspond a 3 ecarts-types.
Aucune donnee reelle sous contrainte n'a ete utilisee : voir docs/EXPERIMENTS.md.
"""


def intervals(ts):
    return [ts[i + 1] - ts[i] for i in range(len(ts) - 1)]


def feats(ts):
    d = intervals(ts)
    n = len(d)
    m = sum(d) / n
    v = sum([(x - m) * (x - m) for x in d]) / n
    return m, (v ** 0.5) / m


class Profile:
    def __init__(self):
        self.mu_m = self.sd_m = self.mu_cv = self.sd_cv = None
        self.n = 0

    def enrol(self, sessions):
        fs = [feats(s) for s in sessions]
        n = len(fs)
        ms = [f[0] for f in fs]
        cs = [f[1] for f in fs]
        self.mu_m = sum(ms) / n
        self.mu_cv = sum(cs) / n
        sm = (sum([(x - self.mu_m) ** 2 for x in ms]) / n) ** 0.5
        sc = (sum([(x - self.mu_cv) ** 2 for x in cs]) / n) ** 0.5
        self.sd_m = max(sm, 0.06 * self.mu_m)      # planchers anti-sur-ajustement
        self.sd_cv = max(sc, 0.06)
        self.n = n
        return self

    def score(self, ts):
        if self.mu_m is None:
            return 0
        m, cv = feats(ts)
        z = max(abs(m - self.mu_m) / self.sd_m, abs(cv - self.mu_cv) / self.sd_cv)
        return min(255, int(z * 32))
