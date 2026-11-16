const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, BorderStyle, AlignmentType, Footer, PageNumber, HeadingLevel, VerticalAlign } = require("docx");
const sizeOf = require("child_process").execSync;
const dims = (f) => sizeOf(`python3 -c "from PIL import Image;im=Image.open('${f}');print(im.width,im.height)"`).toString().trim().split(" ").map(Number);
const FONT = "Times New Roman", K = "000000";
const P = (t, o = {}) => new Paragraph({ spacing: { after: 110, line: 276 }, alignment: o.align || AlignmentType.JUSTIFIED, children: (Array.isArray(t) ? t : [t]).map(x => typeof x === "string" ? new TextRun({ text: x, font: FONT, size: 22, color: K, bold: o.bold, italics: o.italics }) : x), ...(o.p || {}) });
const R = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 22, color: K, bold: o.bold, italics: o.italics });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true, spacing: { before: 280, after: 100 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: K, space: 2 } }, children: [new TextRun({ text: t, font: FONT, size: 26, bold: true, color: K })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 160, after: 60 }, children: [new TextRun({ text: t, font: FONT, size: 23, bold: true, color: K })] });
const img = (f, wIn, cap) => { const [w, h] = dims(f); const W = Math.round(wIn * 96), H = Math.round(W * h / w);
  return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 40 }, keepNext: true, children: [new ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: W, height: H }, altText: { title: cap, description: cap, name: cap } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [R(cap, { size: 19, italics: true })] })]; };
const line = (sz) => ({ style: BorderStyle.SINGLE, size: sz, color: K });
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const table = (rows, widths, opts = {}) => {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => new TableCell({
      width: { size: widths[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      margins: { top: 60, bottom: 60, left: 90, right: 90 },
      borders: { top: line(i === 0 ? 12 : 4), bottom: line(i === 0 || i === rows.length - 1 ? 12 : 4), left: line(4), right: line(4) },
      children: [new Paragraph({ spacing: { after: 0 }, alignment: AlignmentType.LEFT, children: [new TextRun({ text: String(c), font: FONT, size: 19, bold: i === 0, color: K })] })] })) })) });
};
const sp = () => new Paragraph({ spacing: { after: 100 }, children: [] });

// ---------- couverture / en-tête ----------
const logo = fs.readFileSync("assets/logo_fss_official.png");
const head = new Table({ width: { size: 9600, type: WidthType.DXA }, columnWidths: [1700, 7900], rows: [new TableRow({ children: [
  new TableCell({ width: { size: 1700, type: WidthType.DXA }, borders: { top: none, bottom: none, left: none, right: none }, children: [new Paragraph({ children: [new ImageRun({ type: "png", data: logo, transformation: { width: 90, height: 89 }, altText: { title: "Logo officiel", description: "Logo officiel de la Faculté des Sciences de Sfax", name: "logo" } })] })] }),
  new TableCell({ width: { size: 7900, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER, borders: { top: none, bottom: none, left: none, right: none }, children: [
    new Paragraph({ spacing: { after: 20 }, children: [R("Faculté des Sciences de Sfax", { bold: true, size: 26 })] }),
    new Paragraph({ spacing: { after: 20 }, children: [R("Matière : MicroPython (MPI1) · Année universitaire 2026-2027", { size: 21 })] }),
    new Paragraph({ spacing: { after: 0 }, children: [R("Encadrante : Roua Torjmen", { size: 21 })] })] })] })] });

const body = [
  head,
  new Paragraph({ spacing: { before: 200, after: 40 }, border: { top: line(12) }, children: [] }),
  new Paragraph({ alignment: AlignmentType.LEFT, spacing: { before: 60, after: 40 }, children: [R("TACET", { bold: true, size: 52 })] }),
  new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 60 }, children: [R("Autorisation sous contrainte sur un lien furtif à débit constant", { size: 30 })] }),
  new Paragraph({ spacing: { after: 20 }, children: [R("Terminal ESP32 / MicroPython pour ordres irréversibles bancaires et de commandement", { italics: true, size: 21 })] }),
  new Paragraph({ spacing: { after: 200 }, border: { bottom: line(12) }, children: [R("Amal Karaoud · petit rapport scientifique · projet individuel", { size: 21 })] }),

  H1("1. Résumé"),
  P("Un ordre irréversible (virement de grande valeur, libération d’une commande) doit être autorisé par un humain devant un terminal embarqué, sur un lien qu’un adversaire peut observer, alors que cet humain peut être contraint. Les ingrédients de défense sont connus ; la question traitée est plus étroite : peut-on les combiner pour que rien d’observable, ni sur l’appareil, ni sur le fil, ni à l’écran, ne distingue un ordre contraint d’un ordre légitime, tandis que le centre de contrôle réagit correctement ?"),
  P("TACET répond par un terminal ESP32 en MicroPython qui n’émet qu’une trame chiffrée de 64 octets par créneau, ne vérifie aucun code PIN et ne connaît pas le code de contrainte. Le centre (C2) seul décide : EXÉCUTION, LEURRE silencieux ou ATTENTE. Le prototype a été exécuté dans la simulation Wokwi et ses six scénarios donnent les mêmes verdicts que la référence sur ordinateur."),

  H1("2. Problème et justification"),
  P("Les mondes militaire et bancaire partagent un même scénario d’attaque : l’opérateur légitime est menacé et saisit lui-même l’ordre. La double autorisation à deux personnes et le code de contrainte existent, mais chacun fuit séparément : un code de contrainte vérifié localement trahit sa sémantique si le terminal est saisi ; un ordre émis ponctuellement signale par sa seule présence qu’une opération vient d’avoir lieu. Le projet réunit donc quatre domaines pour une même raison : la cryptographie (authentification sans vérification locale), la sécurité des réseaux (analyse de trafic), le comportement (rythme de frappe) et les systèmes répartis (double contrôle au C2)."),

  H1("3. État de l’art et originalité"),
  P("Recherche web effectuée le 16 novembre 2026, non exhaustive. Aucune « première mondiale » n’est revendiquée."),
  table([["Ingrédient", "Existe déjà", "Statut"],
    ["Code PIN de contrainte, alarme silencieuse", "Brevet DAB US 6 679 422 (format proche du PIN normal) ; articles « panic passwords » ; portefeuilles matériels", "Connu"],
    ["Jetons de contrainte dérivés par HMAC", "Protocole CANARY (extension HOTP/TOTP avec contrainte)", "Connu"],
    ["Canal d’alarme silencieuse dans un jeton à mot de passe unique", "Famille de brevets (cités dans un PDF hébergé par le MIT)", "Connu"],
    ["Intégrité à deux personnes", "Doctrine militaire ; produits « dual control »", "Connu"],
    ["Remplissage à débit constant", "Link padding (arXiv 1708.05044) ; Katzenpost", "Connu"],
    ["Terminal sans PIN ni vérificateur ; deux classes de PIN vérifiables seulement au C2, dans une trame fixe à débit constant", "Non trouvé dans cette recherche", "Combinaison, choix de conception"],
    ["Empoisonnement au niveau de la commande, quel que soit l’ordre des opérateurs", "Non trouvé dans cette recherche", "Combinaison, choix de conception"]],
    [3300, 4600, 1700]),
  sp(),

  H1("4. Architecture"),
  ...img("assets/fig_architecture.png", 6.3, "Figure 1. Terminal, canal hostile modélisé et centre de commandement."),
  P("La trame (figure 2) a toujours 64 octets : compteur, texte chiffré de 48 octets par un flux PRF en mode compteur construit sur HMAC-SHA256, et une balise de lien de 12 octets. Le clair contient un type (ordre ou couverture), l’opérateur, la commande, l’action, le montant, le score comportemental, une balise d’opérateur de 16 octets et un remplissage aléatoire. La balise d’opérateur est calculée avec une clé dérivée du PIN réellement saisi : le terminal ne sait donc pas si ce PIN est correct, de contrainte ou faux."),
  ...img("assets/fig_frame.png", 6.3, "Figure 2. Format de trame."),
  ...img("assets/fig_c2_flow.png", 4.7, "Figure 3. Ordre de décision au C2."),
  P("MicroPython est essentiel : machine.Pin et I2C, framebuf pour l’écran SSD1306, hashlib pour HMAC, select.poll pour la console, time.ticks pour l’ordonnancement. Le module hmac étant absent, HMAC-SHA256 est reconstruit et vérifié contre la bibliothèque standard de CPython."),

  H1("5. Montage"),
  ...img("assets/fig_wiring.png", 5.8, "Figure 4. Câblage ESP32 : clavier 4×4, écran OLED I2C, deux LED."),
  table([["Composant", "Broches ESP32", "Rôle"],
    ["Clavier membrane 4×4", "Lignes 32, 33, 25, 26 ; colonnes 27, 23, 19, 18", "Saisie du PIN (6 chiffres), choix des scénarios"],
    ["OLED SSD1306 128×64", "SDA 21, SCL 22, 3V3, GND", "Écran du terminal (ce que voit l’agresseur)"],
    ["LED verte + 330 Ω", "GPIO 4", "Accusé visible par l’agresseur"],
    ["LED rouge + 330 Ω", "GPIO 16", "Verdict du C2, démonstration uniquement"]],
    [2500, 3900, 3200]),
  sp(),

  H1("6. Expériences et résultats"),
  P([R("Statut des données. ", { bold: true }), R("E1 et E5 sont mesurées sur l’implémentation réelle ; E2 est synthétique ; E3 est un modèle analytique avec taille de trame exacte ; la simulation Wokwi est réelle mais le canal est modélisé.")]),
  table([["Essai", "Résultat", "Statut"],
    ["E1 écouteur : ordre ou couverture ?", "51,0 % (contre 100 % sans couverture)", "Mesuré"],
    ["E2 rythme de frappe, seuil 3 écarts-types", "faux positifs 2,0 %, détection 51,7 %, AUC 0,917", "Synthétique"],
    ["E3 coût de la couverture, créneau 1 s", "512 bit/s, attente moyenne 502 ms", "Modèle"],
    ["E5 vol de la clé du terminal et d’une trame", "PIN à 6 chiffres retrouvé hors ligne en 1,9 s", "Mesuré (limite)"],
    ["Tests unitaires", "13 sur 13 réussis", "Mesuré"]],
    [3600, 4300, 1700]),
  ...img("assets/fig_results.png", 6.4, "Figure 5. (a) exactitude de l’écouteur ; (b) rythme de frappe ; (c) latence selon le débit."),
  H2("Simulation Wokwi"),
  P("Le circuit a été chargé et exécuté sur ESP32 simulé avec le micrologiciel MicroPython 1.21. Les six scénarios produisent les verdicts attendus et les mêmes scores comportementaux que la référence sur ordinateur (8 ; 66 et 4 ; 157 et 27). Le terminal affiche invariablement « ORDRE TRANSMIS » (figure 6)."),
  ...img("assets/fig_oled_real.png", 6.4, "Figure 6. Écrans OLED réels de la simulation : S1 exécution, S2 leurre, S3 attente, S4 rejeu, S5 altération, S6 verrouillage."),

  H1("7. Limites"),
  P("La radio est modélisée, non simulée : un matériel réel utiliserait un module LoRa, absent de Wokwi. Le C2 s’exécute sur le même microcontrôleur dans la démonstration. L’opérateur est simulé par un générateur congruentiel déterministe. Le rythme de frappe est un signal faible et ne sert qu’à escalader le risque. Si la clé du terminal et une trame sont volées, un PIN court tombe hors ligne ; une dérivation lente, un élément sécurisé matériel et un PIN plus long sont des pistes, non réalisées. Le code de contrainte reste exploitable seulement si l’opérateur peut le saisir sans se trahir."),
  H1("8. Conclusion"),
  P("TACET montre qu’un terminal minimaliste peut rendre indiscernables, sur l’écran, sur le fil et dans le comportement des accusés, un ordre légitime et un ordre contraint, en déléguant toute la sémantique au centre. La contribution est l’intégration, sa réalisation en environ quatre cents lignes de MicroPython et la mesure honnête de ses limites. Suites : liaison LoRa réelle, élément sécurisé, données comportementales réelles recueillies avec consentement."),

  H1("Références"),
  ...[
    "Brevet US 6 679 422, Automatic teller system and method of marking illegally obtained cash (PIN de contrainte).",
    "CANARY Protocol, coercion-resistant spoken verification, canary-kit (cdn.jsdelivr.net/npm/canary-kit).",
    "Duress Detection for Authentication Attacks Against Multiple Administrators, passwordresearch.com, article 469.",
    "Panic Passwords: Authenticating under Duress (typeset.io).",
    "Spying on the Smart Home: Privacy Attacks and Defenses on Encrypted IoT Traffic, arXiv 1708.05044.",
    "Xuan et al., Analytical and Empirical Analysis of Countermeasures to Traffic Analysis Attacks, ICPP 2003.",
    "Documentation Wokwi, simulation ESP32 (docs.wokwi.com/guides/esp32).",
    "Dépôt du projet : fichiers README, docs/ et tests/ fournis avec ce rapport."
  ].map((t, i) => new Paragraph({ spacing: { after: 50 }, indent: { left: 360, hanging: 360 }, children: [R(`[${i + 1}] ${t}`, { size: 19 })] }))
];
const doc = new Document({ creator: "Amal Karaoud", title: "TACET — petit rapport scientifique",
  styles: { default: { document: { run: { font: FONT, size: 22, color: K } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1153, right: 1153 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, border: { top: line(4) }, children: [R("TACET · Amal Karaoud · Faculté des Sciences de Sfax · 2026-2027 · page ", { size: 17 }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 17, color: K })] })] }) },
    children: body }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync("dist/TACET_rapport.docx", b); console.log("ok", b.length); });
