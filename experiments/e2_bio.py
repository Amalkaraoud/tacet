"""E2 - detection comportementale implicite. DONNEES SYNTHETIQUES (hypotheses dans le code)."""
import os, sys, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))
import tbio as B

R = random.Random(20261116)
N_OPS, N_ENROL, N_TEST = 300, 8, 40
DRIFT = 0.08        # derive de rythme entre sessions (hypothese)
CV0 = 0.18          # variabilite intra-session (hypothese)

def sess(mu, cv, n=7):
    t = [0.0]
    for _ in range(n - 1):
        t.append(t[-1] + max(40.0, R.gauss(mu, mu * cv)))
    return t

def stress(mu0):
    k = R.choice([0.75, 1.35])            # precipite OU hesitant (hypothese)
    return sess(mu0 * k * R.gauss(1, DRIFT), CV0 * 1.5)

def run(n_enrol):
    gen, bad = [], []
    for _ in range(N_OPS):
        mu0 = R.uniform(180, 300)
        p = B.Profile().enrol([sess(mu0 * R.gauss(1, DRIFT), CV0) for _ in range(n_enrol)])
        gen += [p.score(sess(mu0 * R.gauss(1, DRIFT), CV0)) for _ in range(N_TEST)]
        bad += [p.score(stress(mu0)) for _ in range(N_TEST)]
    return gen, bad

def roc(gen, bad):
    out = []
    for thr in (64, 96, 128, 160, 192, 224):
        fpr = sum(g >= thr for g in gen) / len(gen)
        tpr = sum(b >= thr for b in bad) / len(bad)
        out.append({"seuil": thr, "z": thr / 32, "FPR": round(fpr, 4), "TPR": round(tpr, 4)})
    pairs = sum((b > g) + 0.5 * (b == g) for b in bad[:3000] for g in gen[:3000]) / (3000 * 3000)
    return out, round(pairs, 3)

res = {}
for ne in (8, 12, 20):
    g, b = run(ne)
    tab, auc = roc(g, b)
    res["enrol_%d" % ne] = {"table": tab, "AUC": auc}
    print("enrol", ne, "AUC", auc)
    for r in tab: print("  ", r)
os.makedirs("results", exist_ok=True)
json.dump(res, open("results/e2_bio.json", "w"), indent=1)
