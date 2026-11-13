# Monde VJ — Couche 15 : relief géomorphologique et érosion passée

**État : prototype terminé et testé (13 novembre 2026)**  
**Branche expérimentale :** `prototype/couche-15-geomorphologie` (créée depuis `prototype/couche-14-rivieres`) — aucun merge dans `main`.

## Intention validée
Produire un *état géologique initial crédible* avant la simulation du climat et de la végétation, et non calculer de l'érosion en temps réel au cours d'une journée de 2 000 pas. Suspension maintenue des herbivores et carnivores pour consacrer les ressources au paysage et aux interactions météo-hydrologiques.

## Code de la couche 15
- [Prototype standalone HTML (ouvrir hors ligne)](Monde_VJ_Atlas_3D_Couche_15_Relief_Geomorphologique.html)
- [Documentation et méthode](README.md)
- Les fichiers Windows (ZIP) et captures comparatives ont été livrés dans la conversation.

## Périmètre implémenté
- [x] Ancien générateur de dômes conservé pour comparaison A/B à seed identique.
- [x] Nouveau champ de soulèvement en axes montagneux connectés, avec contreforts ramifiés.
- [x] Bruit multi-échelle, sommets non uniformes, modulation des crêtes, variation spatiale de la résistance rocheuse.
- [x] Incision fluviale ancienne : accumulation D4 et pente locale, itérations pendant la génération seulement.
- [x] Relaxation limitée des versants pendant la génération ; quatre styles : alpin, ancien, plateau, mixte.
- [x] Couche 14 : drainage et incision des lits après la géomorphologie, avant l'initialisation des volumes d'eau.
- [x] Mini-carte lithologie/érosion ; contrôles géologie, érosion, crêtes et comparaison.
- [x] Export CSV enrichi : résistance, proximité des crêtes, incision initiale.
- [x] Code météo couche 13 et nuages/pluie des couches 11–12 conservés.
- [x] Faune toujours en pause, sans suppression de son code.
- [x] Tests automatisés, plusieurs seeds, conservation du système et vérification de la reproductibilité.

## Mesures — seed 42, type « massif jeune »
| Indicateur | Résultat |
|---|---:|
| Grille | 200 × 200 cellules = 4 km² |
| Période | 2 000 pas = 24 h |
| Altitude max après rivière | 179,58 m |
| Chaînes structurantes | 2 principales, 4 branches |
| Cellules ayant subi une incision / relaxation nette > 2 cm | 39 646 |
| Décaissement géologique maximal | 3,79 m |
| Volume apparent retiré (avant initialisation physique) | 2,89 Mm³ |
| Cellules en lit de rivière | 1 655 |
| Longueur de chenaux | 16,06 km |
| Écarts montants dans les chenaux | 0 |
| Génération du terrain seule | ~0,25–0,33 s sous Chromium de test |

**Test 2 000 pas continus** : masse d'eau 7,15e-15, énergie 1,33e-16 et matière sèche 2,54e-15 d'erreur relative ; 5 066 cellules végétalisées, 0 herbivore, 0 carnivore au pas 2 000. Aucun changement du champ géologique pendant les pas physiques. Les morphologies alpin, ancien, plateau et mixte sont distinctes et reproductibles.

**Robustesse 4 seeds** : 1, 42, 72026 et 98765 ; toutes conservent des chenaux sans remontée topographique et des invariants physiques à l'initialisation.

## Limites
- Modèle **procédural géomorphologique simplifié**, pas tectonique des plaques ni érosion chronologique calibrée.
- Le « volume retiré » est un indicateur de terrain *initial*, pas un bilan de sédiments transportés pendant la simulation.
- L'hydrologie demeure le moteur discret D4 ; l'étape B (débits réels de rivières) n'est pas commencée.
- L'affichage Canvas a été validé sous Chromium ; WebGL2 matériel reste à valider sous Windows.
- Pas d'érosion évolutive sur des millénaires ; la géologie est figée au cours des journées simulées.

**Statut final :** HTML et ZIP Windows livrés, branche conservée pour validation visuelle utilisateur avant merge.
