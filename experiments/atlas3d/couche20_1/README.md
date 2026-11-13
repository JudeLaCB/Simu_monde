# Monde VJ — Couche 20.1 : fiabilisation physique

**Prototype autonome HTML** issu de la couche 20 ; correctif expérimental réalisé après l'audit du 13 novembre 2026. Les 7 paysages, 7 climats, Random Seed, 6 niveaux atmosphériques, nappes, rivières, cryosphère et végétation sont conservés. La faune reste désactivée.

## Lancement Windows

Double-cliquer sur `Lancer_Monde_VJ_20_1.bat` (ou ouvrir `Monde_VJ_Atlas_3D_Couche_20_1_Fiabilisation_Physique.html` dans Chrome/Edge). Aucune dépendance pour l'application.

## Corrections réalisées

- **P0 : sûreté** — analyse au début et à la fin de chaque pas des stocks de surface, sol, nappe, cryosphère, végétation, vapeur/nuages par altitude, géologie et énergies. Arrêt avec le nom du champ, l'index et la valeur en cas de NaN, Infini, valeur négative ou capacité dépassée. Les écarts globaux de matière sèche, énergie et eau restent surveillés.
- **P1 : infiltration** — conductivité de surface indicatrice de la lithologie, de 2 à 32 mm/h selon la cellule, avec réduction progressive selon la saturation du sol. Ancien plafond uniforme équivalent à 500 mm/h remplacé.
- **P1 : nappes ↔ cours d'eau** — transfert bidirectionnel fondé sur la différence entre charge hydraulique des cellules de nappe voisines et niveau de la rivière ; disparition de la règle de source fondée sur saturation seule. La conductance reste synthétique/non calibrée.
- **P1 : frontières atmosphériques** — dépôt horizontal conservatif **à bords fermés** pour les anciens et nouveaux transports de nuages/vapeur. L'eau n'est plus transmise artificiellement d'Est en Ouest ou du Nord au Sud.

## Limites : chantier encore ouvert

- Le modèle d'atmosphère conserve un seul `airHeat` global et des profils de pression/température diagnostiques, sans thermodynamique locale à six niveaux ; la condensation reste une approximation.
- L'évaporation ne dépend pas encore explicitement du déficit de vapeur et de la couche limite ; la rivière n'utilise pas encore une dynamique hydraulique complète (rugosité, vitesses, sections).
- Les flux n'ont pas encore fait l'objet d'un registre énergétique local indépendant et l'énergie solaire/radiative demeure comptabilisée dans le bilan élargi.
- Les conditions aux limites atmosphériques fermées peuvent accumuler l'humidité contre le bord : choix de cohérence pour une parcelle close, **pas** représentation d'un véritable climat régional ouvert.
- Les coefficients géologiques sont procéduraux, non validés sur des observations réelles.

## Résultats de vérification

- Tests unitaires : charge nulle → flux nul ; nappe gagnante → flux positif ; rivière perdante → flux inverse ; eau conservée.
- Transport atmosphérique : 100 kg injectés au bord Est → 0 kg au bord Ouest ; 100 kg conservés.
- Alertes : NaN, Infinity, stock négatif, dépassement de capacité et `gwCap=NaN` bloquent le **premier pas** sans avance de l'horloge.
- Climats tempéré, aride, tropical, polaire et sécheresse : essais courts sans erreur de conservation ; WebGL2 (SwiftShader/Xvfb) démarré sans erreur JavaScript.
- Essai progressif jusqu'à 1 200 pas : bilans conservés dans les segments terminés, mais **l'essai de 2 000 pas n'a pas été validé** : blocage/limite du processus de test au-delà. L'application complète sous Windows doit être testée.
- Résultats JSON et script Playwright reproductible joints. Le test facultatif requiert Python, `pip install playwright` et `playwright install chromium`.

## Positionnement

**Correctif 20.1 : lot P0 et corrections hydrologiques/frontières P1**. Ce n'est **pas** encore la clôture de toutes les anomalies physiques de l'audit. Ne pas fusionner dans `main` avant recettage Windows et contrôle longue durée.