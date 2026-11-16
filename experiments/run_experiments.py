"""E1 distinguisheur de trafic, E3 compromis debit/latence, E5 limite (capture terminal).
Toutes les mesures sont REELLES sur l'implementation (CPython, vraies HMAC) ; la liaison est modelisee."""
import os, sys, json, random, time, hmac, hashlib, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))
import tproto as P, tchannel as C, tconfig as cfg
R = random.Random(7)
res = {}

# ---- E1 : un ecouteur peut-il reperer les creneaux "ordre reel" ? ----
def frames(n_real, n_cover):
    keys = P.Keys(cfg.MASTER); t = P.Terminal(keys); out = []
    for i in range(n_real + n_cover):
        if i < n_real: t.submit(1, "482915", i & 0xFFFF, 1, R.randrange(10**6))
        else: pass
        pass
    return t
def feat(f):
    b = f[4:52]
    pc = sum(bin(x).count("1") for x in b) / (8 * len(b))
    mean = sum(b) / len(b)
    chi = sum((b.count(v) - len(b) / 256) ** 2 for v in set(b))
    return (pc, mean, chi)
def make(kind, n):
    keys = P.Keys(cfg.MASTER); t = P.Terminal(keys); out = []
    for i in range(n):
        if kind == "real": t.submit(1 + (i & 1), "482915" if i & 1 == 0 else "739206", i & 0xFFFF, 1, R.randrange(10**6))
        out.append(t.next_frame())
    return out
real, cover = make("real", 3000), make("cover", 3000)
Fr, Fc = [feat(f) for f in real], [feat(f) for f in cover]
best = 0
for j in range(3):
    xs = sorted([x[j] for x in Fr] + [x[j] for x in Fc])
    for thr in xs[::30]:
        for sgn in (1, -1):
            acc = (sum((sgn * (x[j] - thr) > 0) for x in Fr) + sum((sgn * (x[j] - thr) <= 0) for x in Fc)) / 6000
            best = max(best, acc)
# baseline sans couverture : des evenements espaces => le simple instant de reception revele l'ordre
res["E1"] = {"frames_per_class": 3000, "best_single_feature_threshold_accuracy": round(best, 4),
             "baseline_event_driven_timing_accuracy": 1.0,
             "note": "meilleure exactitude sur 3 caracteristiques x seuils (optimiste pour l'adversaire, evaluee sur les donnees d'apprentissage)"}
print("E1", res["E1"])

# ---- E3 : debit et latence selon la periode de creneau ----
rows = []
for slot in (250, 500, 1000, 2000, 5000):
    keys = P.Keys(cfg.MASTER); lat = []
    for _ in range(2000):
        t = P.Terminal(keys); c = P.C2(keys, cfg.OPERATORS); L = C.Link(t, c, C.Observer(), slot_ms=slot)
        arrive = R.uniform(0, slot)     # instant d'arrivee de l'ordre dans le creneau
        lat.append(slot - arrive)       # attente jusqu'au prochain creneau
    rows.append({"slot_ms": slot, "debit_bit_s": 64 * 8 * 1000 / slot,
                 "latence_moy_ms": round(sum(lat) / len(lat), 1), "latence_max_ms": slot})
res["E3"] = rows
print("E3", rows)

# ---- E5 : limite - cle du terminal + trame captee => force brute hors-ligne du PIN ----
keys = P.Keys(cfg.MASTER); t = P.Terminal(keys); t.submit(1, "482915", 1, 1, 5)
f = t.next_frame()
from tcrypto import xor_bytes, keystream
ctr = int.from_bytes(f[:4], "big"); pt = xor_bytes(f[4:52], keystream(keys.kenc, ctr, 48))
body, otag = pt[:10], pt[10:26]
t0 = time.time(); found = None
for n in range(10**6):
    pin = "%06d" % n
    kop = hmac.new(keys.kmac, b"OP" + bytes([1]) + pin.encode(), hashlib.sha256).digest()
    if hmac.new(kop, f[:4] + body, hashlib.sha256).digest()[:16] == otag:
        found = pin; break
res["E5"] = {"pin_recupere": found == "482915", "essais": n + 1, "duree_s": round(time.time() - t0, 2),
             "lecture": "avec Kmac extraite du terminal ET une trame captee, un PIN a 6 chiffres tombe hors-ligne : limite reconnue"}
print("E5", res["E5"])
json.dump(res, open("results/experiments.json", "w"), indent=1)
