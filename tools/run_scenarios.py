import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))
import tproto as P, tchannel as C, tconfig as cfg, tscen as S
keys = P.Keys(cfg.MASTER)
t = P.Terminal(keys); c = P.C2(keys, cfg.OPERATORS)
L = C.Link(t, c, C.Observer())
ctx = S.Ctx(L, t, c)
print("profil op1 mu=%.1f sd=%.1f cv=%.3f" % (ctx.prof[1].mu_m, ctx.prof[1].sd_m, ctx.prof[1].mu_cv))
for i, n in enumerate(S.NAMES):
    ev = []
    out = S.run(i, ctx, lambda e: ev.append(e))
    print(n, "->", out, [e.get("bio") for e in ev if "bio" in e])
print("observateur:", L.obs.summary())
