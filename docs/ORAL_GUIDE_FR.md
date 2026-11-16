# Guide de soutenance TACET (15 min) — Amal Karaoud

## Chronométrage
| Diapo | Durée | Message |
|---|---|---|
| 1 | 0:30 | Accroche : un ordre contraint ne doit rien montrer |
| 2 | 1:30 | Trois fuites : appareil, fil, écran |
| 3 | 1:30 | Terminal muet, centre qui décide |
| 4 | 1:30 | Trame fixe de 64 octets, MicroPython |
| 5 | 1:30 | Six verdicts du C2 |
| 6 | 1:00 | Montage ESP32 / Wokwi |
| 7 | 3:00 | **Démo** : S1 exécution, S2 leurre, S3 attente |
| 8 | 1:30 | Mesures et statut des données |
| 9 | 1:00 | Originalité honnête |
| 10 | 1:00 | Limites |
| 11 | 0:30 | Conclusion |

## Démo
Wokwi : touche `D` enchaîne les scénarios. Montrer que l'écran du terminal est identique (« ORDRE TRANSMIS ») et que seule la ligne `[jury] C2` change.
**Secours** (si Wokwi ne charge pas) : `python tools/run_scenarios.py` (sortie de référence identique) ou la diapo 7 (captures réelles).

## Questions probables du jury
1. **Est-ce une première mondiale ?** Non. PIN de contrainte, CANARY, deux personnes, débit constant existent. L'apport est la combinaison et la réalisation.
2. **Pourquoi MicroPython ?** hashlib, framebuf, I2C, select.poll, ticks : tout le terminal tient en ~400 lignes ; HMAC reconstruit.
3. **La radio est-elle simulée ?** Non, modélisée (tchannel.py). Matériel réel : ESP32 + LoRa.
4. **Le C2 est sur le même ESP32 ?** Oui en démo ; en réel, séparé.
5. **Qui tape les PIN ?** Un opérateur scripté (LCG déterministe), pas un humain.
6. **Si la clé du terminal est volée ?** E5 : PIN à 6 chiffres retrouvé hors ligne en 1,9 s avec une trame. Pistes : élément sécurisé, PIN plus long, dérivation lente (non réalisées).
7. **Le rythme de frappe est-il fiable ?** Non : signal faible, données synthétiques, ~2 % de faux positifs. Sert seulement à escalader vers ATTENTE.
8. **Pourquoi 64 octets ?** Une taille unique rend ordre et couverture indiscernables.
9. **Que voit l'agresseur ?** Écran, trames 64 o à 1/s, accusé identique.
10. **Rejeu ?** Compteur strictement croissant côté C2 → DROP_REPLAY.
11. **Pourquoi deux opérateurs ?** Intégrité à deux personnes ; un leurre empoisonne toute la commande.
12. **Que feriez-vous ensuite ?** LoRa réel, élément sécurisé, données de frappe réelles avec consentement.

## Grille d'auto-évaluation sévère (sur 20)
| Critère | Max | Note honnête | Justification / défaut restant |
|---|---|---|---|
| Originalité vérifiée, sans fausse première | 3 | 2,5 | Combinaison, recherche non exhaustive |
| Rigueur technique (code, tests, protocole) | 4 | 3,5 | 13 tests ; crypto non auditée |
| Simulation Wokwi convaincante et honnête | 3 | 2,5 | Exécutée ; projet non sauvegardé/partagé |
| Mesures reproductibles | 3 | 2,5 | E2 synthétique |
| Dossier / dépôt GitHub professionnel | 3 | 2 | Dépôt prêt mais non publié (en attente d'accord) |
| Présentation et rapport | 3 | 2,5 | Département et titre officiel à confirmer |
| Défense des limites | 1 | 1 | Limites explicites |
| **Total** | **20** | **16,5** | Pas de note 20/20 annoncée : défauts listés ci-dessus |
