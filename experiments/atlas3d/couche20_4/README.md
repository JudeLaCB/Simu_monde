# Monde VJ — Couche 20.4 · Consolidation du cycle de l'eau

[**Ouvrir le prototype HTML autonome**](Monde_VJ_Atlas_3D_Couche_20_4_Cycle_Eau.html) (Chrome / Edge, Windows, hors ligne).

Couche expérimentale dérivée de 20.3, qui conserve le rendu nuageux doux, les **six strates**, les **frontières atmosphériques périodiques**, l'interface simplifiée, les nappes, les rivières et la faune en pause.

## Modifications

- **Thermodynamique verticalisée :** chaque strate dispose d'une énergie thermique et d'une température propres, avec échanges de chaleur internes conservatifs et bilan énergétique global unique.
- **Condensation :** réponse exponentielle de la vapeur saturante à la température (forme de Tetens), **normalisée empiriquement** sur la réserve d'humidité préexistante. Ce n'est pas un calibrage absolu d'une colonne d'air sec.
- **Précipitations :** les gouttes et les flocons disposent de stocks propres en transit à chaque niveau ; chute progressive, réévaporation des gouttes et fonte éventuelle des flocons avant le sol, échanges de chaleur latente comptabilisés.
- **Évaporation et transpiration :** dépendance à l'humidité de la strate basse, à la température, au vent et aux stocks d'eau disponibles.
- **Nuages :** position graphique déduite de la masse condensée dans les strates et d'une topographie locale lissée (environ 250 m), **sans formule globale 'sommet le plus haut + décalage'**. Les nuages élevés peuvent sortir du champ de la caméra : dézoomer si nécessaire.

## Invariants

200×200 cellules de 10 m = 4 km² ; 2 000 pas = 1 jour ; masse d'eau comptabilisée dans surface + sol + nappe + biosphère + vapeur + nuages + pluie/neige en transit + cryosphère. Les précipitations en chute ne sont plus déposées instantanément au sol. Frontières fermées pour les rivières et nappes.

## Résultats

| Scénario (seed 42) | Durée continue | Erreur relative eau | Erreur relative énergie |
|---|---:|---:|---:|
| Mixte, tempéré | 2 000 pas | 3,49e-15 | 6,64e-16 |
| Montagnes, tropical | 150 pas | 6,53e-15 | 7,97e-16 |
| Hautes montagnes, polaire | 120 pas | 4,03e-15 | 7,99e-16 |
| Montagnes, tropical, WebGL2/SwiftShader | 120 pas | 2,26e-15 | 9,30e-16 |

En tropical (150 pas), environ **2,58 millions de kg** de précipitations se sont formées ; **2,46 millions de kg** ont atteint le sol et **0,102 million de kg** se sont réévaporées en altitude. Le solde reste notamment en transit.

## Limites importantes

Capacités thermiques fixes, pression hydrostatique indicative sans dynamique, vents paramétrés, microphysique empirique ; pas de gouttes déviées horizontalement pendant leur chute, pas d'océan ouvert ni de saisonnalité météorologique calibrée. La conservation globale **ne valide pas indépendamment les lois physiques**. Les tests de 2 000 pas ne sont pas encore répétés en climat extrême ni sur GPU Windows matériel.

Voir [PROGRESS.md](PROGRESS.md). Ne pas fusionner vers main avant essais matériels et calibration.
