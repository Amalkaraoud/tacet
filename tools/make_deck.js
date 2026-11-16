const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; pres.author = "Amal Karaoud"; pres.title = "TACET";
const F = "Calibri", H = "Cambria", K = "000000", W = "FFFFFF";
const line = (s, x, y, w, h = 0, wt = 1) => s.addShape(pres.ShapeType.line, { x, y, w, h, line: { color: K, width: wt } });
const T = (s, t, o) => s.addText(t, Object.assign({ fontFace: F, color: K, margin: 0, isTextBox: true, valign: "top" }, o));
function base(title, n, notes) {
  const s = pres.addSlide(); s.background = { color: W };
  T(s, title, { x: 0.7, y: 0.45, w: 11.9, h: 0.9, fontFace: H, fontSize: 30, bold: true });
  line(s, 0.7, 1.35, 11.9, 0, 1.5);
  T(s, "TACET · Amal Karaoud · Faculté des Sciences de Sfax", { x: 0.7, y: 7.0, w: 8, h: 0.3, fontSize: 10 });
  T(s, String(n), { x: 11.9, y: 7.0, w: 0.7, h: 0.3, fontSize: 10, align: "right" });
  s.addNotes(notes); return s;
}
// 1 couverture
let s = pres.addSlide(); s.background = { color: W };
s.addImage({ path: "assets/logo_fss_official.png", x: 0.7, y: 0.6, w: 1.1, h: 1.086 });
T(s, "Faculté des Sciences de Sfax", { x: 2.0, y: 0.75, w: 8, h: 0.4, fontSize: 18, bold: true });
T(s, "MicroPython (MPI1) · 2026-2027 · Encadrante : Roua Torjmen", { x: 2.0, y: 1.2, w: 9, h: 0.4, fontSize: 14 });
line(s, 0.7, 2.3, 11.9, 0, 3);
T(s, "TACET", { x: 0.7, y: 2.6, w: 11.9, h: 1.4, fontFace: H, fontSize: 80, bold: true });
T(s, "Un ordre contraint ne doit rien montrer.", { x: 0.7, y: 4.1, w: 11.9, h: 0.7, fontFace: H, fontSize: 32, italic: true });
T(s, "Autorisation sous contrainte sur un lien furtif à débit constant · ESP32 / MicroPython", { x: 0.7, y: 4.9, w: 11.9, h: 0.5, fontSize: 18 });
line(s, 0.7, 6.3, 11.9, 0, 1);
T(s, "Amal Karaoud", { x: 0.7, y: 6.45, w: 6, h: 0.5, fontSize: 20, bold: true });
s.addNotes("Accroche (30 s). Se présenter, nommer l’encadrante. Dire la phrase du titre et poser la question : comment un terminal peut-il ne rien révéler quand l’opérateur est menacé ?");

// 2 problème
s = base("Le problème : l’opérateur peut être contraint", 2, "Scénario : virement de grande valeur ou libération d’une commande. L’agresseur observe l’écran, écoute le lien, et force l’opérateur à saisir lui-même l’ordre. Deux fuites classiques : le PIN de contrainte vérifié localement, et l’ordre émis ponctuellement.");
T(s, "Trois fuites à fermer", { x: 0.7, y: 1.7, w: 6, h: 0.5, fontSize: 22, bold: true });
T(s, [
 { text: "Sur l’appareil : un PIN de contrainte vérifié localement trahit sa sémantique si le terminal est saisi.", options: { bullet: true, breakLine: true } },
 { text: "Sur le fil : un ordre émis ponctuellement signale qu’une opération a lieu.", options: { bullet: true, breakLine: true } },
 { text: "À l’écran : tout message différent d’un ordre normal alerte l’agresseur.", options: { bullet: true } }], { x: 0.7, y: 2.3, w: 7.2, h: 3.2, fontSize: 20, paraSpaceAfter: 12 });
T(s, "Question", { x: 8.6, y: 1.7, w: 4, h: 0.5, fontSize: 22, bold: true });
s.addShape(pres.ShapeType.rect, { x: 8.6, y: 2.3, w: 4.0, h: 3.0, fill: { color: W }, line: { color: K, width: 2 } });
T(s, "Peut-on rendre un ordre contraint indiscernable d’un ordre légitime — écran, fil, accusé — tout en alertant le centre ?", { x: 8.85, y: 2.5, w: 3.5, h: 2.6, fontFace: H, fontSize: 20, italic: true, valign: "middle" });

// 3 idée
s = base("L’idée : un terminal muet, un centre qui décide", 3, "Le terminal ne vérifie aucun PIN et ne connaît pas le code de contrainte. La balise d’opérateur est calculée avec le PIN réellement saisi ; seul le C2 sait la comparer. Une trame de 64 octets par créneau, vraie ou de couverture.");
s.addImage({ path: "assets/fig_architecture.png", x: 0.7, y: 1.6, w: 7.6, h: 7.6 * 0.38 });
T(s, [
 { text: "Terminal : aucun vérificateur, aucun secret de PIN.", options: { bullet: true, breakLine: true } },
 { text: "Lien : 1 trame de 64 octets par seconde, toujours.", options: { bullet: true, breakLine: true } },
 { text: "C2 : seul à connaître PIN normal et PIN de contrainte.", options: { bullet: true, breakLine: true } },
 { text: "Écran : « ORDRE TRANSMIS » dans tous les cas.", options: { bullet: true } }], { x: 8.6, y: 1.7, w: 4.0, h: 4.5, fontSize: 18, paraSpaceAfter: 12 });

// 4 trame
s = base("Une trame fixe de 64 octets, vraie ou de couverture", 4, "Compteur, texte chiffré 48 octets par flux PRF en mode compteur sur HMAC-SHA256, balise de lien de 12 octets. Les trames de couverture ont exactement la même taille et la même cadence.");
s.addImage({ path: "assets/fig_frame.png", x: 0.7, y: 1.8, w: 11.9, h: 11.9 * 0.2 });
T(s, "MicroPython : hashlib, machine.Pin, I2C, framebuf, select.poll, time.ticks. Le module hmac est absent : HMAC-SHA256 reconstruit, vérifié contre CPython.", { x: 0.7, y: 5.0, w: 11.9, h: 1.0, fontSize: 18 });

// 5 décision C2
s = base("Le centre décide : six verdicts", 5, "Ordre de décision : couverture, balise de lien, rejeu, vérification PIN, rythme de frappe, double autorisation. Le leurre empoisonne toute la commande quel que soit l’ordre des opérateurs. L’accusé descendant est identique pour tous les résultats.");
s.addImage({ path: "assets/fig_c2_flow.png", x: 0.9, y: 1.5, w: 4.2, h: 4.2 * 1.18 });
T(s, [
 { text: "EXÉCUTION : deux opérateurs distincts dans la fenêtre.", options: { bullet: true, breakLine: true } },
 { text: "LEURRE : PIN de contrainte, silencieux.", options: { bullet: true, breakLine: true } },
 { text: "ATTENTE : rythme de frappe anormal.", options: { bullet: true, breakLine: true } },
 { text: "REJEU / ALTÉRATION : trame abandonnée.", options: { bullet: true, breakLine: true } },
 { text: "VERROUILLAGE : trois échecs.", options: { bullet: true } }], { x: 6.0, y: 1.8, w: 6.6, h: 4.5, fontSize: 20, paraSpaceAfter: 12 });

// 6 montage
s = base("Montage ESP32 et simulation Wokwi", 6, "Montage : clavier 4x4, OLED SSD1306 I2C, deux LED. Radio non simulée : modèle de canal. Le C2 tourne sur le même microcontrôleur dans la démonstration.");
s.addImage({ path: "assets/fig_wiring.png", x: 0.7, y: 1.6, w: 7.2, h: 7.2 * 0.62 });
T(s, [
 { text: "ESP32 DevKit, MicroPython 1.21.", options: { bullet: true, breakLine: true } },
 { text: "Clavier 32,33,25,26 / 27,23,19,18.", options: { bullet: true, breakLine: true } },
 { text: "OLED SDA 21, SCL 22.", options: { bullet: true, breakLine: true } },
 { text: "LED verte GPIO 4, rouge GPIO 16.", options: { bullet: true } }], { x: 8.3, y: 1.8, w: 4.3, h: 3.5, fontSize: 18, paraSpaceAfter: 10 });

// 7 captures réelles
s = base("Résultat réel : six scénarios dans Wokwi", 7, "Captures réelles de l’écran OLED simulé. Le terminal affiche toujours ORDRE TRANSMIS ; seule la ligne [jury] C2 change. S1 exécution, S2 leurre, S3 attente, S4 rejeu, S5 altération, S6 verrouillage.");
s.addImage({ path: "assets/fig_oled_real.png", x: 0.7, y: 1.6, w: 9.0, h: 9.0 * 0.5 });
T(s, "Mêmes verdicts et mêmes scores (8 ; 66 et 4 ; 157 et 27) que la référence sur ordinateur.", { x: 10.0, y: 1.8, w: 2.6, h: 3.5, fontSize: 16 });

// 8 mesures
s = base("Mesures et statut des données", 8, "Insister sur l’honnêteté : E2 est synthétique, E3 est un modèle, E5 est une vraie limite. Le seuil à 3 écarts-types donne environ 2 % de faux positifs.");
s.addImage({ path: "assets/fig_results.png", x: 0.7, y: 1.6, w: 7.6, h: 7.6 * 0.31 });
const hb = { type: "solid", color: K, pt: 1.5 }, cb = { type: "solid", color: K, pt: 0.75 };
const cell = (t, b) => ({ text: t, options: { bold: b, fontFace: F, fontSize: 13, color: K, border: [cb, cb, cb, cb], valign: "middle" } });
s.addTable([[cell("Essai", 1), cell("Résultat", 1), cell("Statut", 1)],
 [cell("E1 écouteur"), cell("51,0 %"), cell("Mesuré")],
 [cell("E2 rythme"), cell("FP 2,0 %, AUC 0,917"), cell("Synthétique")],
 [cell("E3 couverture"), cell("512 bit/s"), cell("Modèle")],
 [cell("E5 vol de clé"), cell("PIN en 1,9 s"), cell("Mesuré (limite)")],
 [cell("Tests"), cell("13 / 13"), cell("Mesuré")]], { x: 0.7, y: 4.4, w: 11.9, colW: [4, 4.4, 3.5], rowH: 0.38 });

// 9 originalité
s = base("Originalité : une combinaison, pas une première mondiale", 9, "Recherche web du 16 novembre 2026, non exhaustive. Les ingrédients sont connus. La contribution : terminal sans vérificateur, trames fixes à débit constant, empoisonnement au niveau commande, comportement identique sur écran, fil et accusé.");
T(s, "Déjà connu", { x: 0.7, y: 1.7, w: 5.6, h: 0.5, fontSize: 22, bold: true });
T(s, [
 { text: "PIN de contrainte, alarme silencieuse (brevets)", options: { bullet: true, breakLine: true } },
 { text: "Jetons de contrainte CANARY", options: { bullet: true, breakLine: true } },
 { text: "Intégrité à deux personnes", options: { bullet: true, breakLine: true } },
 { text: "Remplissage à débit constant", options: { bullet: true, breakLine: true } },
 { text: "Dynamique de frappe", options: { bullet: true } }], { x: 0.7, y: 2.3, w: 5.6, h: 3.5, fontSize: 19, paraSpaceAfter: 10 });
line(s, 6.65, 1.7, 0, 4.2, 1);
T(s, "Notre apport", { x: 7.0, y: 1.7, w: 5.6, h: 0.5, fontSize: 22, bold: true });
T(s, [
 { text: "Terminal sans PIN ni vérificateur", options: { bullet: true, breakLine: true } },
 { text: "Trames chiffrées fixes, débit constant", options: { bullet: true, breakLine: true } },
 { text: "Empoisonnement de la commande entière", options: { bullet: true, breakLine: true } },
 { text: "Même comportement : écran, fil, accusé", options: { bullet: true } }], { x: 7.0, y: 2.3, w: 5.6, h: 3.5, fontSize: 19, paraSpaceAfter: 10 });

// 10 limites
s = base("Limites assumées", 10, "Dire les limites avant que le jury ne les trouve. Chaque limite a une piste de remédiation, non réalisée.");
const lim = [["Radio", "modélisée ; réel : module LoRa"], ["C2", "sur le même ESP32 en démonstration"], ["Opérateur", "simulé par un LCG déterministe"], ["Rythme de frappe", "synthétique ; signal faible"], ["Vol de clé + trame", "PIN à 6 chiffres retrouvé hors ligne"]];
lim.forEach((r, i) => { const y = 1.7 + i * 0.95; line(s, 0.7, y, 11.9, 0, 0.75);
  T(s, r[0], { x: 0.7, y: y + 0.2, w: 3.5, h: 0.6, fontSize: 22, bold: true });
  T(s, r[1], { x: 4.4, y: y + 0.22, w: 8.2, h: 0.6, fontSize: 20 }); });
line(s, 0.7, 6.45, 11.9, 0, 0.75);

// 11 conclusion
s = pres.addSlide(); s.background = { color: W };
T(s, "Ce qui reste visible : rien.", { x: 0.7, y: 1.7, w: 11.9, h: 1.3, fontFace: H, fontSize: 48, bold: true });
line(s, 0.7, 3.2, 11.9, 0, 3);
T(s, [
 { text: "Un terminal minimal, environ quatre cents lignes de MicroPython.", options: { bullet: true, breakLine: true } },
 { text: "Six scénarios vérifiés sur ESP32 simulé.", options: { bullet: true, breakLine: true } },
 { text: "Limites mesurées et dites.", options: { bullet: true, breakLine: true } },
 { text: "Suites : LoRa réel, élément sécurisé, données de frappe réelles.", options: { bullet: true } }], { x: 0.7, y: 3.6, w: 11.9, h: 2.4, fontSize: 22, paraSpaceAfter: 10 });
T(s, "Merci · Amal Karaoud", { x: 0.7, y: 6.4, w: 8, h: 0.5, fontSize: 20, bold: true });
s.addNotes("Conclusion (1 min). Reprendre la phrase : ce qui reste visible, c’est rien. Inviter les questions.");
pres.writeFile({ fileName: "dist/TACET_presentation.pptx" }).then(() => console.log("ok"));
