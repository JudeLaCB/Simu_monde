# Monde VJ — Audit de cohérence physique et numérique

**Version auditée :** couche 20, `Monde_VJ_Atlas_3D_Couche_20_Strates_Atmospheriques.html`  
**Date :** 13 novembre 2026  
**Périmètre :** génération du relief, hydrologie de surface, nappes, météorologie, transport atmosphérique 3D simplifié, énergie, cryosphère, plantes, contrôles numériques et couplages.  
**Méthode :** inspection de la source de 3 453 lignes, vérification dimensionnelle des équations et constantes, tests de conservation et de positivité, tests synthétiques ciblés avec sondes injectées *uniquement dans le navigateur de test*. **Le HTML du simulateur n'a pas été modifié.**

## Synthèse exécutive

> **Le système est un simulateur environnemental exploratoire à stocks conservés, et non encore un modèle physique calibré.** Les bilans d'eau et d'énergie sont très bien fermés sur les trajectoires testées, mais certains échanges sont des lois empiriques et l'audit révèle un défaut critique de surveillance des valeurs non finies.

**Ce qui est réellement acquis :** grille 200×200 (4 km², 10 m/cellule), horloge 2 000 pas/jour (43,2 s/pas), transferts bilatéraux explicites des stocks d'eau (surface, humidité du sol, nappes, vapeur, nuages, neige et glace), suivi d'énergie gravitationnelle/thermique/latente/chimique, drainage génératif du terrain, six stocks atmosphériques verticaux, reproductibilité par seed sur les cas déjà validés. Animaux désactivés volontairement.

**Ce qui n'est pas encore acquis :** conservation robuste *face aux valeurs non finies*, dynamique hydrostatique/thermique atmosphérique 3D, fermeture locale de l'énergie, saturation hygrométrique fondée sur la thermodynamique, cycle du carbone, écoulements de rivière en débit physique, conditions aux limites homogènes, paramètres hydrologiques calibrés.

### Priorités d'audit

| Niveau | Constat vérifié | Effet | Localisation du code |
|---|---|---|---|
| **P0 — Défaut de sûreté** | Une `NaN` dans l'aquifère rend masse/énergie `NaN` **sans déclencher l'alerte** | Les tests de conservation peuvent échouer silencieusement | `hydroTick`, ~L1920–1935 |
| **P1 — Hydrologie** | Infiltration maximale uniforme : **500 mm/h** | Sols et ruissellements trop perméables, indépendamment des roches | `SOIL_INFILTRATION_M_STEP`, L369 ; `hydroTick`, ~L1887 |
| **P1 — Nappes/rivières** | « Source » possible dans une cellule saturée sans différence de charge ; pas de débit de base réaliste par les berges vers un cours d'eau mouillé | Sources et pérennité des rivières mal représentées | `stepGroundwater16`, ~L1840–1855 |
| **P1 — Conditions aux limites** | Atmosphère périodique Est/Ouest et Nord/Sud, hydrologie/géologie à bords fermés | L'humidité peut « téléporter » à travers un bord, notamment sur une côte | `atm20Transport`, ~L501–541 ; `transportAtmosphere`, L1592 |
| **P1 — Thermodynamique** | Une seule `airHeat` globale ; température/pression des six strates **diagnostiques** | Pas de bilan de chaleur ni de stabilité résolu par couche | L425–427, `atm20LayerTemperature`, L447 ; `stepClimate`, L1732 |
| **P1 — Condensation** | « Saturation » linéaire en température et en kg/cellule ; pas de dépendance thermodynamique correcte à pression et volume | Condensation/pluie peu calibrables, notamment sous froid tropical ou altitude | `stepCloudsAndRain20`, ~L552–562 |
| **P1 — Surface-énergie** | Évaporation sans rétroaction directe de l'humidité relative et du vent ; nuages n'atténuent pas l'énergie solaire locale des sols | Réponses climatiques trop prescrites, effets de brouillard/couvert nuageux biaisés | `hydroTick`, ~L1902–1918 ; `stepClimate`, L1732 |
| **P2 — Hydraulique** | Débit de rivières basé sur la différence de niveau × coefficient, non sur la section/rugosité hydraulique | Régime de rivière et temps de réponse qualitatifs | `exchange`, L1873 |
| **P2 — Biogéochimie** | Croissance végétale : matière sèche puisée dans `substrateKg`, pas de stock de CO₂ atmosphérique | Pas de cycle du carbone : biomasse « créée » à partir du substrat | `stepVegetation`, ~L1058–1098 |
| **P2 — Cryosphère** | Changement d'état latent fermé, mais neige sans albédo rétroactif, tassement, sublimation ni isolation | Climat de montagne/neige schématique | `stepCryosphere18`, L1643 ; `stepClimate`, L1732 |
| **P2 — Climat/géologie** | Forçages climatiques et reliefs procéduraux, faux littoral fermé, saisons stylisées sur 20 jours | Bons scénarios comparatifs, pas de prévisions locales | `VJ_CLIMATES19`, L3244 ; `priorityDrainage14`, L694 |

## 1. Vérifications quantitatives réalisées

### 1.1 Conservation et états positifs

Banc d'essai : **Montagnes, seed 42**, sept climats, 100 pas chacun, navigateur Chromium en mode Canvas de secours, calcul physique intact. Les résultats sont consignés dans `Monde_VJ_Audit_Physique_Couche20_Tests.json`.

| Climat | Pas | Erreur de masse relative | Erreur d'énergie relative | Stock négatif détecté | JS |
|---|---:|---:|---:|---|---|
| Tempéré | 100 | 1,28e-15 | 1,33e-16 | Non | 0 |
| Aride | 100 | 1,45e-14 | 1,33e-16 | Non | 0 |
| Tropical | 100 | 3,14e-15 | 1,33e-16 | Non | 0 |
| Mousson | 100 | 3,64e-15 | 2,66e-16 | Non | 0 |
| Polaire | 100 | 1,65e-15 | 1,06e-15 | Non | 0 |
| Sécheresse intense | 100 | 8,51e-16 | 3,98e-16 | Non | 0 |
| Méditerranéen | 100 | 1,10e-15 | 0 | Non | 0 |

Les tableaux contrôlés : eau de surface, sol, aquifère, vapeur et nuages des 6 niveaux. Les stocks minimaux sont non négatifs et finis pour ces essais.

**Stress supplémentaires (indépendants) :**

- Polaire : 500 pas, erreurs eau 6,60e-15 / énergie 9,32e-16 ; air à −3,44 °C, sol de −6,95 à +0,20 °C, environ 46,53 Mkg de neige et 20,51 Mkg de glace, sans alerte.
- Sécheresse intense : 500 pas, erreurs eau 6,98e-15 / énergie 1,33e-16 ; air à 30,90 °C, sol de 25,28 à 36,11 °C, aucune pluie sur la fenêtre testée, sans alerte.
- Mousson : un essai prolongé a été interrompu par les ressources du navigateur ; **non validé à 500 pas** dans cet audit.
- Le précédent test de développement de la couche 20 avait validé 2 000 pas sous *Montagnes + Tropical* ; il n'a **pas** été répété indépendamment ici.

### 1.2 Défaut critique du contrôleur de sécurité — reproduction

Sonde sur une copie **temporaire en mémoire** du HTML : affectation de `gwWater[20200]=NaN`, puis exécution d'un pas physique.

| Variable observée | Résultat |
|---|---|
| Pas exécuté | 1 |
| Masse totale | `NaN` |
| Énergie totale | `NaN` |
| Erreur JavaScript | Aucune |
| Alerte physique visible | **Non** |

**Cause :** l'expression `Math.abs(NaN)>seuil` est toujours fausse. Le test d'erreur ne vérifie pas `Number.isFinite`, et omet les minima/finis de `water`, `soilWater`, `gwWater`, `vaporKg`, `cloudKg`, `atm20Vapor`, `atm20Cloud`. Il surveille certaines autres collections (neige, glace, biomasse), mais une valeur `NaN` y passerait également inaperçue avec une simple comparaison `<0`.

**Correction P0 :** validation *finie et bornée* des grandeurs globales et de tous les stocks, avec diagnostic de la cellule, du réservoir, du pas et du dernier sous-solveur actif ; ne pas seulement calculer une erreur relative.

### 1.3 Infiltration : ordre de grandeur incompatible avec les sols courants

`SOIL_INFILTRATION_M_STEP = 0.012 × TIME_FACTOR = 0.006 m/pas` avec `SECONDS_PER_STEP = 43.2 s`.

\[
I_{\max}=\frac{0,006\;m}{43,2\;s}=0,0001389\;m/s=500\;mm/h.
\]

C'est un **plafond local instantané**, pas une infiltration réelle de 12 m chaque jour : les stocks et la capacité du sol la limitent. Néanmoins, à titre de comparaison, la FAO donne typiquement 1–5 mm/h en argile, 10–20 mm/h en limon/loam et 20–30 mm/h en sol sableux-limoneux. **La loi est indépendante de la lithologie et de l'humidité relative jusqu'à saturation.**

**Correction :** conductivité d'infiltration de surface par cellule (dépendante du sol), puis loi de capacité et de saturation avec ruissellement. Conserver une régulation numérique du flux, mais pas un coefficient physique commun.

### 1.4 Nappe ↔ rivière : expérience à gradient nul

Cellule d'un chenal sélectionnée automatiquement, aquifère saturé (`gwWater=gwCap`) ; tous les autres stocks souterrains vides, transport latéral désactivé pour isoler ce mécanisme, recharge désactivée.

| Expérience | Eau superficielle initiale | Tête de nappe − altitude du terrain | Eau émergente |
|---|---:|---:|---:|
| Lit sec | 0 mm | 0 m | **151,2 kg** |
| Lit avec 8 mm d'eau | 8 mm | 0 m | **0 kg** |

Cette émergence en lit sec provient d'un seuil `saturation>.995 && water<.002`, **sans gradient hydraulique démontré**. Inversement, l'algorithme n'exprime pas l'écoulement des berges vers un lit mouillé ; le calcul se fait uniquement avec la charge de l'aquifère *sous la cellule de rivière*, dont la tête est bornée au niveau du terrain. Les vrais cours d'eau gagnants/perdants dépendent de la charge de la nappe environnante par rapport à la hauteur de la rivière.

**Correction :** flux bidirectionnel `Q = C_bed × (H_aquifère voisin − H_rivière)` avec section et conductance du lit, plus conservation locale et limites de stockage ; pas de source liée à la seule saturation.

### 1.5 Frontières atmosphériques : transit artificiel Est → Ouest

Sonde indépendante : injecter **100 kg de vapeur** dans la cellule Est `x=199`, appliquer le transport horizontal, vent dirigé vers l'est. **100 kg** restent conservés ; au moins **72,05 kg** réapparaissent immédiatement sur le côté Ouest (`x≤10` sur la même rangée). La masse restante atteint d'autres rangées via le cisaillement.

La conservation est parfaite, mais il s'agit d'un domaine en **tore atmosphérique**, alors que le terrain, les rivières et la nappe représentent une parcelle non périodique à bords fermés. Ces conditions incompatibles peuvent affecter les précipitations sous le vent, particulièrement dans le profil littoral.

**Correction :** choisir explicitement (a) un domaine régional périodique pour **tous** les champs compatibles, ou (b) des bords atmosphériques ouverts avec humidité/enthalpie entrantes imposées et des **budgets des flux aux frontières**. Pour le monde de 2 km, (b) est scientifiquement plus défendable.

### 1.6 Vent : unité physique mesurée

Sous la configuration par défaut (seed 42), sondage d'un échantillon réparti sur la grille : vitesse moyenne horizontale ≈ **0,223 m/s**, extrêmes **0,067–0,333 m/s** en basse couche. L'instrumentation convertit directement les cellules/pas en m/s avec 10 m/cellule et 43,2 s/pas.

Ce n'est pas un bug numérique à lui seul, mais des **vents très faibles** au regard de nombreux épisodes météorologiques réels. Les profils de régime et le cisaillement en altitude peuvent les renforcer ; la distribution réelle doit être calibrée et documentée avant d'interpréter orographie, convection ou vitesse des nuages.

## 2. Audit par domaine

### Géosphère et relief — **prototype géomorphologique acceptable**

- ✔ Crêtes, altitudes, érodabilité procédurale, incision ancienne et rivières sont générées **avant** l'initialisation physique. Cela respecte le choix de ne pas faire évoluer l'érosion sur des jours.
- ◼ Pas de bilan de sédiment pendant l'« érosion passée », pas de tectonique ou contrainte lithologique issue de mesures : **pas de reconstitution géologique prédictive**.
- ◼ Drainage D4 strictement descendant : nombreuses dépressions fermées potentielles, sans résolution automatique des seuils de débordement. Le réseau peut s'interrompre dans des minima artificiels.

### Hydrosphère — **stocks solides, débits simplifiés**

- ✔ Eau conservée entre surface/sol/nappe/atmosphère et phase solide sur les cas testés.
- ⚠ Écoulement de surface `exchange` fonction de la différence de niveau et d'une fluidité adimensionnelle : pas de section, rugosité Manning, régime torrentiel ni vitesse propre de l'eau.
- ⚠ Infiltration de surface excessive et homogène (cf. 1.3), recharge profonde également empirique.
- ⚠ Nappe 2D libre, paramétrée par une seule valeur de conductivité par cellule ; écoulement latéral inspiré de Darcy mais **débit vers lit de rivière incorrect** (cf. 1.4).
- ◼ Littoral = bassin fermé d'eau douce, ni océan, ni salinité, ni marées. C'est un choix de périmètre déjà identifié.

### Atmosphère — **six stocks verticaux réels, dynamique de l'air non résolue**

- ✔ `atm20Vapor` et `atm20Cloud` ont réellement 6×40 000 cellules ; le transport vertical/horizontal conserve la masse. La couche 20 n'est donc pas seulement une décoration graphique.
- ⚠ **Pas de masse d'air sec transportée** : pression du panneau `1013,25 exp(-z/8434)` et températures `tempAir()−0,0065z+correction` sont diagnostiques.
- ⚠ Une seule chaleur d'air globale `airHeat` : aucune équation thermodynamique indépendante par étage. Des mouvements de vapeur entre étages ne transportent pas d'enthalpie localement.
- ⚠ Saturation calculée par `clamp(10+1,7(T+15−refroidissement),8,110) × poids_niveau` : la thermodynamique impose une pression de vapeur saturante *non linéaire* liée à T, puis un rapport de mélange qui dépend de la pression, de l'air sec et du volume de couche.
- ⚠ Le champ de vent est une déformation heuristique des vents de fond par le relief, **pas** une solution de continuité et de quantité de mouvement. Le mélange vertical est modulé par `windLift`, soleil et des poids empiriques.
- ⚠ Limites périodiques (cf. 1.5) ; précipitation transférée directement des six étages au terrain, sans temps de chute ni évaporation sous les nuages.
- ◼ Nuages principalement représentés par un overlay 2D projeté ; altitude physique répartie, mais volume graphique non résolu sur six niveaux.

### Thermodynamique et énergie — **comptabilité fermée, thermique à recalibrer**

- ✔ `latentEnergy`, `phaseEnergy18`, `solarEnergy`, `radiatedEnergy` et les potentiels sont suivis : beaucoup de transferts physiques sont à somme nulle.
- ⚠ `radiatedEnergy` est un **cumul de rayonnement évacué**, pourtant compté dans `totalEnergy`. De même, l'« apport solaire » est retiré d'un stock initial gigantesque `solarEnergy=1,2×10^17 J`. La conservation globale vérifiée valide principalement une **comptabilité incluant sources et puits**, non un équilibre thermique indépendant du domaine.
- ⚠ Le réservoir `airHeat` a une capacité totale **1,2×10^12 J/K**, soit **300 000 J/(m²·K)**. Pour une atmosphère réellement modélisée de 0 à 4 km, une estimation grossière à 1 kg/m³ et 1 005 J/(kg·K) donnerait ≈ **4,02×10^6 J/(m²·K)**, soit plus de **13 fois** la capacité présente. Ce chiffre est indicatif : le modèle global actuel peut représenter une couche thermique « effective », mais il ne peut alors pas être interprété comme la chaleur complète des six étages.
- ⚠ Les changements d'énergie gravitationnelle (écoulement, nappe, transport vertical) sont souvent injectés/retirés du seul `airHeat` comme réservoir de compensation. Pas de bilan local des dissipations, travail mécanique, énergie cinétique du vent ou stockage thermique de l'eau.
- ⚠ L'évaporation dépend essentiellement du stock liquide, de la température du sol et d'un taux du profil climatique ; pas de calcul de déficit de pression de vapeur, résistance aérodynamique, vent ou humidité relative. La fraction solaire transmise au sol ne tient pas compte de l'opacité des nuages de chaque cellule.

### Cryosphère — **bilan de phase utile, physique neigeuse rudimentaire**

- ✔ Réservoirs neige/glace séparés et chaleur latente de fusion comptabilisée ; fonte vers surface et gel réciproque.
- ◼ Fonte selon sol, ensoleillement et disponibilité énergétique ; pas de couche thermique spécifique neige/glace, ni albédo rétrodiffusif, ni dépôt de givre, ni sublimation, ni compactage, ni isolation thermique. La neige ne crée pas encore une boucle climatique complète.

### Biosphère — **écologie expérimentale, non cycle biogéochimique**

- ✔ Biomasse, eau végétale, stress et reproduction par graines, masse sèche et énergie chimique suivies.
- ⚠ Le gain de biomasse prend du `substrateKg` plutôt que du carbone atmosphérique ; il n'y a pas de bilan CO₂/O₂/nutriments réellement découplés. La photosynthèse est donc un mécanisme *schématique* de fixation de matière sèche/énergie.
- ◼ Les animaux sont volontairement désactivés : **aucun résultat des présents essais ne garantit la conservation ou stabilité après leur réactivation**.

## 3. Plan de correction recommandé — avant d'ajouter de nouvelles couches

### Lot 0 — Fiabiliser l'audit numérique (**P0**)

1. Vérifier `Number.isFinite` sur tous les stocks, énergies, flux, températures et bilans ; imposer les bornes (positivité, capacités, stocks d'air et de nuage).
2. Instrumenter un **registre des flux** entre réservoirs : flux source/sortie par pas et budget par sphère, indépendant de la simple somme finale.
3. Séparer `E_domaine` et `E_externe` : vérifier `ΔE_domaine = E_solaire_entrant − E_IR_sortant + autres flux de bord` plutôt que conserver un stock solaire fictif dans le domaine.
4. Tests unitaires d'anomalies volontaires (`NaN`, `Infinity`, eau négative, dépassement de capacité, masse soustraite sans contrepartie) ; arrêter et identifier le module responsable.

**Critère d'acceptation :** une seule perturbation non finie doit déclencher une alerte **au premier pas**, avec identifiant de réservoir et cellule.

### Lot 1 — Recalibrer le cycle de l'eau (**P1**)

1. Infiltration paramétrée par lithologie, état hydrique et capacité (Horton/Green–Ampt simplifié ou Ksat variable).
2. Échange nappe–rivière bidirectionnel **par gradient de charge aux berges**, conductance hydraulique du lit et correction de la règle d'affleurement à saturation.
3. Clarifier la frontière atmosphérique : recommandation **conditions latérales ouvertes** avec bilan eau/enthalpie et humidité extérieure, ou annoncer explicitement une carte périodique complète.
4. Débits de rivière et temps de transit calculés en unités physiques et validés sur un plan incliné et un bassin fermé.

**Critère d'acceptation :** zéro émergence souterraine sans forçage hydraulique dans un test isolé ; infiltration dans la gamme de référence propre au type de sol ; toutes les masses restent correctement comptabilisées, y compris aux limites.

### Lot 2 — Rendre l'atmosphère réellement thermodynamique (**P1**)

1. Masse d'air sec par niveau et couche (équation hydrostatique / densité, modèle simplifié adapté à 4 km).
2. Température et enthalpie **par niveau et cellule**, avec flux de chaleur résolus verticalement.
3. Saturation `q_sat(T,p)` via pression de vapeur saturante, condensation et évaporation avec chaleur latente locale.
4. Flux d'évaporation fondé sur différence hygrométrique, radiation nette et vent ; atténuation solaire par couverture nuageuse.
5. Vent calibré en m/s ; continuité de la masse d'air, advection conservatrice et conditions aux limites cohérentes.

**Critère d'acceptation :** couches verticales thermiques autonomes, colonnes stables/inversées détectées physiquement et bilans thermo-hydriques vérifiés **par couche**, pas uniquement globalement.

### Lot 3 — Détailler sans précipitation (**P2**)

- Temps de chute pluie/neige et évaporation des gouttes sous nuage ; transfert entre niveaux.
- Rétroaction de neige sur albédo et isolation du sol.
- Cycle carbone/nutriments/CO₂, avant toute réactivation de la faune.
- Calibration des scénarios climatiques à partir de séries de références ; saisons plus lentes et frontières océaniques uniquement si elles deviennent utiles au périmètre 2×2 km.

## 4. Matrice de vérification à installer avant tout nouveau prototype

| Expérience synthétique | Comportement physique attendu |
|---|---|
| Plan incliné inondé | Ruissellement dirigé vers l'aval ; eau fermée conservée ; flux comparables à une solution de référence |
| Deux cellules de nappe, charges identiques | Flux latéral nul |
| Deux cellules de nappe, gradient inversé | Flux change exactement de sens, pas de débit imposé |
| Rivière entourée de berges à charge supérieure | Débit de base positif en eau, y compris avec rivière déjà mouillée |
| Colonne atmosphérique sans forçage, profil stable | Pas de convection artificielle ; enthalpie conservée par étage |
| Atmosphère saturée et sous-saturée | Evaporation dépend du déficit hygrométrique ; condensation conforme à T et p |
| Domaine à frontière ouverte | Tout flux entrant/sortant est mesuré et additionné au bilan |
| Alternance neige/gel/fonte sans soleil | Enthalpie et stocks de phase cohérents |
| Forçage `NaN` dans chaque réservoir | Alerte immédiate avec origine précise |
| 7 climats × plusieurs seeds × 2 000 pas | Pas de `NaN`, pas de valeur négative, bilans contrôlés ; tests supplémentaires sur 20+ jours pour les oscillations saisonnières stylisées |

## 5. Décision proposée

**Ne pas recommencer Monde VJ à zéro.** L'architecture des réservoirs existants, le générateur du relief, la reproductibilité des seeds, la visualisation et les contrôles de masse sont des acquis. Il serait en revanche prématuré d'ajouter une nouvelle grande fonctionnalité physique avant de corriger le Lot 0 et les anomalies majeures du Lot 1.

Je recommande de conserver intact le prototype Couche 20 et de créer une branche **« Audit & fiabilisation »** ; réaliser les tests instrumentés en premier, puis seulement engager le recalibrage de l'hydrologie et de la thermodynamique verticale. Ne pas réactiver les animaux tant que les bilans par sous-système ne sont pas robustes.

---

### Sources externes de référence utilisées pour les contrôles d'ordre de grandeur

- FAO, *Infiltration rate and infiltration test* : https://www.fao.org/4/s8684e/s8684e0a.htm
- USGS, *Ground Water and Streams* : https://pubs.usgs.gov/circ/circ1139/htdocs/natural_processes_of_ground.htm
- NOAA, *Air-sea flux handbook / saturation vapor pressure* : https://downloads.psl.noaa.gov/BLO/Air-Sea/wcrp_wgsf/flux_handbook/fluxhandbook_NOAA-TECH%20PSD-311v3.pdf
- UC Davis, *Properties of Dry Air* : https://climate.ucdavis.edu/ATM241Spring2020/ATM241-Spring2020-Lecture03.pdf

### Reproductibilité

- Résultats bruts : `Monde_VJ_Audit_Physique_Couche20_Tests.json`.
- Banc de tests : `audit_physics20.py` (instrumente une copie du HTML **en mémoire**, sans modification du fichier livré) et `audit_physics20_nan.py` (test de robustesse de la surveillance).
- Certaines validations de 2 000 pas citées proviennent de la documentation de développement antérieure : elles sont séparées explicitement des nouveaux tests de cet audit.