"""Figures noir et blanc du dossier TACET (aucun gris, aucune couleur, aucune ombre)."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "DejaVu Serif"],
                     "axes.edgecolor": "black", "text.color": "black", "axes.labelcolor": "black",
                     "xtick.color": "black", "ytick.color": "black", "savefig.facecolor": "white"})
OUT = os.path.join(os.path.dirname(__file__), "..", "assets"); os.makedirs(OUT, exist_ok=True)
LW = 1.2

def box(ax, x, y, w, h, t, fs=9, lw=LW, fw="normal", ls="-"):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=lw, ec="black", ls=ls))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, fontweight=fw)

def arr(ax, p, q, t=None, ls="-", fs=8, dy=0.12):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, lw=LW, color="black", ls=ls))
    if t: ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, t, ha="center", fontsize=fs)

# ---------- F1 architecture ----------
fig, ax = plt.subplots(figsize=(10, 4.6)); ax.set_xlim(0, 20); ax.set_ylim(0, 9.2); ax.axis("off")
box(ax, 0.3, 1.2, 5.2, 6.6, "", lw=1.6)
ax.text(2.9, 7.45, "TERMINAL (ESP32 / MicroPython)", ha="center", fontsize=9, fontweight="bold")
box(ax, 0.7, 5.6, 4.4, 1.2, "Clavier 4x4\nPIN 6 chiffres, non verifie ici", 8)
box(ax, 0.7, 3.9, 4.4, 1.3, "Rythme de frappe\nscore comportemental 0..255", 8)
box(ax, 0.7, 2.2, 4.4, 1.3, "Ordonnanceur a debit constant\ntrame de 64 o : ordre OU couverture", 8)
box(ax, 7.3, 2.6, 5.4, 4.2, "", lw=1.6)
ax.text(10.0, 6.45, "CANAL HOSTILE (modele)", ha="center", fontsize=9, fontweight="bold")
box(ax, 7.7, 4.6, 4.6, 1.3, "Observateur passif\n(instant, taille) seulement", 8)
box(ax, 7.7, 3.0, 4.6, 1.3, "Adversaire actif\nrejeu / alteration", 8, ls="--")
box(ax, 14.7, 1.2, 5.0, 6.6, "", lw=1.6)
ax.text(17.2, 7.45, "C2 (banque / etat-major)", ha="center", fontsize=9, fontweight="bold")
box(ax, 15.1, 5.6, 4.2, 1.2, "Tag de lien, anti-rejeu,\ndechiffrement", 8)
box(ax, 15.1, 3.9, 4.2, 1.3, "PIN normal / PIN contrainte\n(seul detenteur)", 8)
box(ax, 15.1, 2.2, 4.2, 1.3, "Double controle 2 operateurs\nEXECUTE / DECOY / HOLD", 8)
arr(ax, (5.5, 3.0), (7.3, 4.2), "trame 64 o"); arr(ax, (12.7, 4.6), (14.7, 4.6), "meme trame")
arr(ax, (2.9, 5.6), (2.9, 5.2)); arr(ax, (2.9, 3.9), (2.9, 3.5))
ax.text(10, 0.5, "Le terminal affiche toujours \"ORDRE TRANSMIS\" : la semantique de contrainte n'existe que cote C2.",
        ha="center", fontsize=8.5, style="italic")
fig.savefig(f"{OUT}/fig_architecture.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- F2 trame ----------
fig, ax = plt.subplots(figsize=(10, 2.5)); ax.set_xlim(0, 64); ax.set_ylim(0, 4.2); ax.axis("off")
parts = [(0, 4, "ctr"), (4, 48, "chiffre (48 o)"), (52, 12, "tag lien")]
for x, w, t in parts: box(ax, x, 2.4, w, 1.2, t, 9)
ax.text(32, 4.0, "Trame : 64 octets, taille fixe", ha="center", fontsize=9, fontweight="bold")
cl = [(4, 1, "T"), (5, 1, "op"), (6, 2, "cmd"), (8, 1, "act"), (9, 4, "param"), (13, 1, "bio"), (14, 16, "tag operateur (16)"), (30, 22, "remplissage aleatoire (22)")]
for x, w, t in cl: box(ax, x, 0.5, w, 1.2, t, 6.3 if w < 3 else 8, lw=1.0)
ax.text(4, 1.95, "clair (48 o), avant chiffrement par flux PRF-CTR", fontsize=8, style="italic")
fig.savefig(f"{OUT}/fig_frame.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- F3 decision C2 ----------
fig, ax = plt.subplots(figsize=(10, 5.6)); ax.set_xlim(0, 20); ax.set_ylim(0, 11); ax.axis("off")
steps = [("Trame recue", 10, 10), ("Tag de lien valide ?", 10, 8.6), ("ctr > dernier ctr ?", 10, 7.2),
         ("Dechiffrer ; type = couverture ?", 10, 5.8), ("Tag operateur : PIN normal / contrainte / aucun ?", 10, 4.4),
         ("Score comportemental >= seuil ?", 10, 3.0), ("Deux operateurs distincts OK ?", 10, 1.6)]
for t, x, y in steps: box(ax, x - 4.2, y - 0.5, 8.4, 1.0, t, 8.5)
for i in range(len(steps) - 1): arr(ax, (10, steps[i][2] - 0.5), (10, steps[i + 1][2] + 0.5), dy=0)
side = [(8.6, "non : DROP_TAMPER"), (7.2, "non : DROP_REPLAY"), (5.8, "oui : COVER"), (4.4, "aucun : FAIL (3 -> LOCKED)"),
        (3.0, "oui : HOLD silencieux"), (1.6, "oui : EXECUTE ; non : PENDING")]
for y, t in side:
    arr(ax, (14.2, y), (15.2, y), dy=0); ax.text(15.3, y, t, va="center", fontsize=8.5)
ax.text(15.3, 3.7, "contrainte : DECOY silencieux", fontsize=8.5, va="center")
ax.text(0.2, 0.3, "DECOY et HOLD sont silencieux : l'acquittement vu par le terminal est identique.", fontsize=8.5, style="italic")
fig.savefig(f"{OUT}/fig_c2_flow.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- F4 cablage ----------
d = json.load(open(os.path.join(os.path.dirname(__file__), "..", "wokwi", "diagram.json")))
pins = [("R1", "GPIO32"), ("R2", "GPIO33"), ("R3", "GPIO25"), ("R4", "GPIO26"), ("C1", "GPIO27"), ("C2", "GPIO23"),
        ("C3", "GPIO19"), ("C4", "GPIO18")]
fig, ax = plt.subplots(figsize=(10, 6.2)); ax.set_xlim(0, 20); ax.set_ylim(0, 12.4); ax.axis("off")
box(ax, 7.6, 1.0, 4.8, 10.4, "", lw=1.8); ax.text(10, 11.0, "ESP32-DevKitC", ha="center", fontsize=10, fontweight="bold")
box(ax, 0.4, 5.6, 4.2, 6.0, "", lw=1.4); ax.text(2.5, 11.2, "Clavier 4x4", ha="center", fontsize=9, fontweight="bold")
for i, (p, g) in enumerate(pins):
    y = 10.4 - i * 0.65
    ax.text(4.4, y, p, ha="right", va="center", fontsize=8.5); ax.plot([4.6, 7.6], [y, y], color="black", lw=1)
    ax.text(7.8, y, g, va="center", fontsize=8.5)
box(ax, 0.4, 1.4, 4.2, 3.4, "", lw=1.4); ax.text(2.5, 4.4, "OLED SSD1306 (I2C 0x3C)", ha="center", fontsize=9, fontweight="bold")
for i, (p, g) in enumerate([("SDA", "GPIO21"), ("SCL", "GPIO22"), ("VCC", "3V3"), ("GND", "GND")]):
    y = 3.7 - i * 0.55
    ax.text(4.4, y, p, ha="right", va="center", fontsize=8.5); ax.plot([4.6, 7.6], [y, y], color="black", lw=1)
    ax.text(7.8, y, g, va="center", fontsize=8.5)
box(ax, 15.2, 6.2, 4.4, 2.2, "", lw=1.4); ax.text(17.4, 8.0, "LED verte (agresseur)", ha="center", fontsize=9, fontweight="bold")
ax.text(17.4, 7.0, "GPIO4 - 330 ohm - LED - GND", ha="center", fontsize=8.5)
box(ax, 15.2, 3.2, 4.4, 2.2, "", lw=1.4); ax.text(17.4, 5.0, "LED rouge (C2, demo)", ha="center", fontsize=9, fontweight="bold")
ax.text(17.4, 4.0, "GPIO16 - 330 ohm - LED - GND", ha="center", fontsize=8.5)
ax.plot([12.4, 15.2], [7.3, 7.3], color="black", lw=1); ax.plot([12.4, 15.2], [4.3, 4.3], color="black", lw=1)
fig.savefig(f"{OUT}/fig_wiring.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# ---------- F5 resultats ----------
R = json.load(open(os.path.join(os.path.dirname(__file__), "..", "results", "experiments.json")))
B = json.load(open(os.path.join(os.path.dirname(__file__), "..", "results", "e2_bio.json")))
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3))
a = axs[0]; a.bar([0, 1], [100, R["E1"]["best_single_feature_threshold_accuracy"] * 100], width=0.5, color="white", edgecolor="black", hatch="///", lw=1.2)
a.axhline(50, color="black", ls="--", lw=1); a.set_xticks([0, 1]); a.set_xticklabels(["sans\ncouverture", "TACET"], fontsize=8.5)
a.set_ylabel("exactitude de l'ecouteur (%)", fontsize=8.5); a.set_ylim(0, 105); a.set_title("(a) distinguer ordre / couverture", fontsize=9)
a.text(1, 54, "%.1f %%" % (R["E1"]["best_single_feature_threshold_accuracy"] * 100), ha="center", fontsize=8.5)
b = axs[1]; T = B["enrol_12"]["table"]
b.plot([t["FPR"] * 100 for t in T], [t["TPR"] * 100 for t in T], "k-o", mfc="white", lw=1.2, ms=5)
for t in T: b.annotate("z=%g" % t["z"], (t["FPR"] * 100, t["TPR"] * 100), textcoords="offset points", xytext=(5, -9), fontsize=7.5)
b.set_xlabel("faux positifs (%)", fontsize=8.5); b.set_ylabel("detection (%)", fontsize=8.5); b.set_title("(b) rythme de frappe (synthetique)", fontsize=9)
c = axs[2]; E3 = R["E3"]
c.plot([e["debit_bit_s"] for e in E3], [e["latence_moy_ms"] for e in E3], "k-s", mfc="white", lw=1.2, ms=5)
for e in E3: c.annotate("%d ms" % e["slot_ms"], (e["debit_bit_s"], e["latence_moy_ms"]), textcoords="offset points", xytext=(4, 5), fontsize=7.5)
c.set_xscale("log"); c.set_xlabel("debit de couverture (bit/s)", fontsize=8.5); c.set_ylabel("latence moyenne (ms)", fontsize=8.5); c.set_title("(c) cout de la couverture", fontsize=9)
for a_ in axs:
    for s in ("top", "right"): a_.spines[s].set_visible(False)
    a_.tick_params(labelsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_results.png", dpi=220, bbox_inches="tight"); plt.close(fig)
print("ok")
