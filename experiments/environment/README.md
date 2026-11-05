# Monde VJ — Prototypes autonomes d'environnement

Ces fichiers HTML sont des expériences indépendantes du moteur Python `src/simu_monde/core`. Ils se lancent sans installation, dans un navigateur moderne. Ils préparent une éventuelle migration des lois environnementales dans le moteur principal.

## Versions

- **V2.1b — [Reliefs localisés, massifs et bassins](v2_1b_reliefs_localises.html)** : état de référence, conservé tel quel dans `main` (commit `41506a8`). Terrain procédural reproductible, eau de surface finie, écoulement gravitationnel dissipatif, conservation de l'eau et bilan d'énergie simplifié.
- **V2.2 — [Évaporation et rétention](v2_2_evaporation_retention.html)** : ajoute le stockage local d'eau dans le sol et un réservoir atmosphérique, sans retirer ou modifier V2.1b.

## Règles nouvelles de V2.2

- **Infiltration** : maximum 12 mm d'eau équivalente par cellule et par pas, limité par l'eau de surface et la place encore disponible dans le sol.
- **Capacité de rétention** : curseur 0–100 %, représentant une capacité de stockage par cellule comprise entre 0 et 0,8 m d'eau équivalente. C'est une *capacité*, et non un coefficient de ruissellement ou un taux de réémission.
- **Évaporation** : curseur 0–1 mm/pas pour l'eau de surface exposée ; si la surface est sèche, le sol humide peut évaporer à 35 % de cette vitesse. Les taux sont volontairement accélérés pour observer des changements en quelques centaines de pas (1 pas = 1 seconde simulée) et ne constituent pas une loi climatique calibrée.
- **Atmosphère** : réservoir de masse global qui reçoit toute l'eau évaporée. **Pas encore de condensation, de pluie, ni de mouvement spatial de vapeur**.
- **Énergie** : l'écoulement et l'infiltration dissipent l'énergie gravitationnelle en chaleur ; l'évaporation utilise une **réserve thermique initiale finie** et transfère de l'énergie vers une réserve latente. La gravité de la vapeur est comptée à une altitude de référence simplifiée. Ce modèle est un bilan comptable explicite, **pas** un modèle thermodynamique ou météorologique validé.

## Bilans

```text
W_totale = W_surface + W_sol + W_atmosphere = constante

E_totale = E_potentielle_gravitationnelle + E_thermique + E_latente = constante
```

Les valeurs sont vérifiées numériquement à chaque pas. L'énergie thermique ne peut pas être puisée indéfiniment : quand elle est insuffisante, l'évaporation s'arrête.

## Comparaisons à réaliser

1. Seed 42, 30 % d'eau, relief « Massifs et lacs », rétention 60 %, évaporation 0,15 mm/pas : observer l'eau de surface, du sol et de l'atmosphère après 500 pas.
2. Sur V2.2, choisir **0 % de rétention et 0 mm/pas d'évaporation** : la trajectoire d'eau de surface reproduit exactement V2.1b pour des paramètres initiaux identiques.
3. Tester indépendamment la rétention seule et l'évaporation seule pour identifier leurs effets.

## Frontière d'architecture

Ces prototypes n'implémentent ni organismes, ni pluie, ni eau souterraine mobile, ni minéraux. Aucun code de l'ancien simulateur écologique n'est modifié par leur ajout. Le futur système d'environnement Python doit préserver le monde en mètres, la seed, le pas de temps fixe, l'indépendance du rendu et les tests d'invariants.


## Versions supplémentaires sur cette branche

- **V2.3 — [Reconnaissance des paysages](v2_3_paysages.html)** : classification indicatrice des lacs, marécages, montagnes, vallées, plateaux et plaines par état local et composantes connexes. La lecture géographique ne modifie pas les équations hydrologiques.
- **V2.4 — [Cycle jour / nuit](v2_4_jour_nuit.html)** : 1 000 pas par jour, dont 500 éclairés ; température globale de l'atmosphère et température de sol par cellule ; chauffage solaire progressif, échanges thermiques sol/air et voisins, refroidissement radiatif et évaporation dépendante de la température.

## Bilans et limites de V2.4

- `W_total = W_surface + W_sol + W_atmosphere` demeure constant.
- `E_comptabilisée = E_gravitationnelle + E_sensible_sol_air + E_latente + E_solaire_restante + E_rayonnement_sortant` demeure constante dans le **système de comptabilité élargi**.
- Le Soleil est un réservoir fini d'énergie initiale ; quand celui-ci est épuisé, le jour continue d'être annoncé par l'horloge mais n'apporte plus de chaleur. Le rayonnement thermique est conservé comme énergie émise, sans être réinjecté artificiellement.
- L'horloge est `1000 pas = 24 h`; les coefficients d'écoulement et d'évaporation par pas sont des approximations, **pas** une hydrodynamique ni un modèle atmosphérique calibrés. L'évaporation maximale par défaut est passée de `0.15 mm/pas` (V2.3) à `0.004 mm/pas` pour permettre un bilan latent et thermique cohérent avec les ordres de grandeur de la nouvelle journée.
- Pas encore de pluie, condensation, vent, nuages ni conduction verticale dans le sol.
- Le core Python historique sous `src/` n'est pas modifié : les prototypes restent des fichiers HTML autonomes.
- Tests manuels automatisés dans Chromium : 2 000 pas sur configuration standard, reproductibilité exacte après reset, contrôles de masse et d'énergie, variantes de rayonnement/évaporation, vue des températures et mise en page mobile.


## V2.5 — Végétation conditionnée par une humidité durable

- Fichier : [v2_5_vegetation.html](v2_5_vegetation.html). Le moteur V2.4 est conservé séparément, sans changement.
- 100 × 100 cellules, 10 m × 10 m chacune ; distribution de graines dormantes déterminée par la seed (70 % initialement). **Les organismes ne surgissent pas spontanément de matière inerte** : les graines dormantes sont une condition initiale, sans masse de graine détaillée.
- L'humidité locale est suivie par référence exponentielle (coefficient 0,035/pas). Une cellule ne peut germer que lorsque l'humidité du sol reste suffisante et peu fluctuante pendant **160 pas consécutifs** (réglable 60–500), avec faible submersion, pente modérée et température de 4–38 °C.
- La germination et la croissance exploitent la lumière du Soleil pendant les 500 pas de jour. Aucun arbre, forêt ou prairie n'est posé par le générateur ; les cellules végétalisées apparaissent au cours des pas.
- La biomasse sèche prélève la masse dans un **substrat nutritif local fini** (28–72 kg par cellule) ; la mort/décomposition locale restitue la matière à ce substrat. Une partie plafonnée de l'énergie solaire est convertie en énergie chimique de biomasse ; le reste chauffe l'air ou le sol. Les réservoirs chimiques et nutritifs sont des approximations, pas une stœchiométrie du carbone ou de la photosynthèse.
- Pour ce premier laboratoire, la croissance **ne prélève pas encore explicitement l'eau** du réservoir de sol. L'humidité agit comme facteur limitant ; l'ajout ultérieur d'absorption et de transpiration devra transférer eau et énergie sans rompre les bilans.
- Pas de reproduction, succession écologique, fixation de carbone atmosphérique, cycle des minéraux détaillé, météo complète ou plantes intelligentes. Le monde ne reçoit aucune matière externe.

### Invariants supplémentaires

```text
W_total = W_surface + W_sol + W_atmosphere                   = W_initial
M_seche = substrat_local + biomasse_vegetale                 = M_seche_initiale
E_totale = E_grav + E_chaleur + E_latente + E_solaire_restant
           + E_rayonnement_sortant + E_chimique_vegetale     = E_initiale
```

### Vérifications Chromium

- Seed 42, paramètres par défaut : 0 cellule végétalisée au pas 120 ; environ 949 au pas 350 ; 996 au pas 500 ; environ 979 au pas 1 000. Ce sont des **résultats du scénario**, pas des objectifs codés dans le programme.
- Reset puis 350 pas : biomasse identique ; 0 % de graines : zéro germination ; absence de lumière : zéro croissance ; absence de rétention du sol : zéro croissance.
- Testés : peu d'eau, beaucoup d'eau, forte croissance et densité totale de graines ; erreurs relatives de masse d'eau, de matière sèche et d'énergie inférieures à 1e-9 sur les scénarios vérifiés.
- Mode sans graines : mêmes valeurs d'eau, températures et énergie que V2.4 au pas 350, à l'identique pour les observables comparées.
- Tests réalisés dans le navigateur sur le **prototype HTML autonome**. Cela ne constitue pas une intégration dans le core Python et ne valide pas un modèle biologique réaliste.


## V2.6 — Herbivores avec perceptrons multicouches individuels

- Prototype : [v2_6_herbivores.html](v2_6_herbivores.html). Expérience autonome issue de V2.5 : l'ancien moteur Python et les prototypes archivés ne sont pas modifiés.
- Population initiale paramétrable (0 à 120, 50 par défaut), chaque individu disposant d'une position continue en mètres, direction, âge, eau corporelle, matière sèche structurelle et énergie chimique stockée.
- **Capteurs locaux** : à gauche, devant et à droite, sondes des ressources végétales, de l'eau et des obstacles ; besoins internes d'énergie et d'hydratation. Pas de vision globale ni de téléportation.
- **Contrôleur** : réseau 12 entrées → 8 neurones `tanh` → 2 sorties (rotation et vitesse) ; génome initial tiré par seed. Aucun code de navigation vers une plante, lac, ou point le plus proche. Le contrôle reste identique pendant la vie.
- **Réflexes au contact** : ingestion de biomasse seulement dans la cellule occupée ; boisson seulement dans la même cellule si eau de surface accessible. Le réflexe n'implique pas de stratégie de recherche.
- **Métabolisme** : prélève de l'énergie chimique animale et transfère une masse équivalente (densité simplifiée 18 MJ/kg) vers le substrat local et l'énergie dissipée vers la chaleur. Les pertes physiologiques d'eau retournent à l'eau du sol. Lors de la mort, restitution immédiate de l'eau, de la matière et de l'énergie : la décomposition n'est **pas encore** réaliste.
- **Naissance** : possible uniquement après une maturité minimale et avec de bonnes réserves, par division des stocks parentaux de matière, d'eau et d'énergie ; copie des connexions neuronales avec mutation paramétrable. La reproduction ne crée pas de ressources. **Évolution générationnelle**, pas encore de renforcement/apprentissage individuel.
- Les animaux initiaux sont explicitement une **condition initiale** : leur matière sèche et leur eau sont prélevées sur des stocks existants lors de la génération du monde. Ce n'est pas une émergence spontanée de la vie.
- Cap de 150 individus pour garder un prototype navigateur réactif ; les lois physiques précédentes de V2.5 sont inchangées.

### Bilans supplémentaires

```text
W = W_surface + W_sol + W_atmosphere + W_corps_animaux
M_seche = substrat + biomasse_vegetale + masse_structurelle_animale + reserves_animales/18 MJ.kg^-1
E = E_grav + E_thermique + E_latente + E_solaire + E_rayonnement + E_plantes + E_animaux
```

La variable `initialEnergy` est fixée après les allocations initiales de stocks animaux. Les transfers entre masse, énergie chimique et chaleur sont explicitement équilibrés. Ce **bilan comptable idéalisé** n'est pas une simulation exacte de respiration, carbone, oxygène, ni chimie physiologique.

### Contrôles Chromium (prototype HTML)

- Seed 42, 50 herbivores initialement : **19 vivants, 16 naissances cumulées** après 3 300 pas dans les essais effectués.
- Après 1 600 pas, `reset → 1 600 pas` produit les mêmes individus, gènes et états à l'identique ; aucune erreur JavaScript.
- Avec **0 herbivores**, les observables physiques et végétales comparées à V2.5 restent *bit-à-bit identiques* à 300 pas.
- Scénarios de stress : 120 animaux/2 000 pas ; pas d'apport solaire/1 700 pas ; rétention du sol nulle/900 pas ; aucune graine/1 350 pas. Conservation de l'eau, de la matière sèche et de l'énergie dans la tolérance relative 1e-9, sans stocks négatifs dans les scénarios contrôlés.
- Avec 0 graine ou 0 soleil, population éteinte dans les essais correspondants. Pas de débordement horizontal à 390 pixels.
- Tests navigateur réalisés localement, **pas** des tests unitaires du core Python.

### Limites et suite possible

Les paramètres physiologiques sont expérimentaux. Les stratégies efficaces ne sont pas garanties par une évolution sélectionnée si les niches sont trop difficiles, et l'apparition d'intelligence n'est pas démontrée. À étudier : trajectoires des individus, génomes parent/descendance, durée des populations, absorption et transpiration réelles par les plantes, décomposition différée, cycle carbone/oxygène et mécanismes évolutifs plus robustes.


## V2.7 — Nuages, pluies, transpiration et sélection des végétaux

**Prototype autonome :** [v2_7_nuages_pluie_vegetation_evolutive.html](v2_7_nuages_pluie_vegetation_evolutive.html). Cette expérimentation HTML reprend la V2.6 et **ne modifie pas** le simulateur Python historique ni les versions HTML archivées.

### Eau atmosphérique locale
- L'atmosphère dispose désormais d'un champ **vapeur** et d'un champ **nuages** (100×100 cellules de 10×10 m, kg/cellule), transportés par un vent simplifié changeant progressivement de direction. Pour éviter les pertes d'eau en bord de carte, **les bordures atmosphériques sont périodiques** ; le sol garde ses bordures imperméables.
- Le réservoir atmosphérique global affiché est la **somme vapeur + eau liquide suspendue dans les nuages**. La condensation, déclenchée lorsque la vapeur dépasse un seuil de saturation local dépendant de la température et du relief, transforme vapeur en nuage et **libère la chaleur latente dans l'air**. Les nuages peuvent se ré-évaporer quand l'air est sous-saturé.
- Les précipitations n'apparaissent que lorsque l'eau liquide nuageuse atteint un seuil. Elles transfèrent de l'eau de l'atmosphère vers la surface et l'énergie potentielle de chute vers la chaleur. Curseur « Précipitations » (0 % désactive, sans contourner le réservoir).
- **Pas encore** de calcul volumique de nuages, température atmosphérique par cellule, aérosols, humidité relative calibrée, vrai moteur de vent, saisons, météo réaliste.

### Végétation autonome et sélection
- La **germination** réclame une humidité localement stable sur la durée demandée ; les **plantes adultes** ne dépendent plus de ce streak et disposent d'une inertie physiologique face au manque d'eau. Une sécheresse **prolongée** peut encore provoquer leur dépérissement.
- Leurs **racines prélèvent de l'eau dans le réservoir du sol**, stockent une petite quantité dans les plantes, puis les feuilles **transpirent** vers la vapeur atmosphérique en consommant de la chaleur et en transférant de l'énergie latente et gravitationnelle.
- Chaque cellule porte quatre traits végétaux héritables (tolérance à la sécheresse, usage de l'eau, amplitude de tolérance thermique, vitesse de croissance). Des graines se dispersent localement depuis les plantes matures et peuvent muter. **La sélection vient des différences de survie/reproduction, sans fonction de score ni succès garanti**.
- Chaque graine possède une **masse sèche de 4 g** : elle est prélevée sur le substrat au départ ou sur la biomasse parentale lors de la reproduction ; la matière et l'énergie chimiques restent comptabilisées.
- Le substrat sec, la chimie, le métabolisme et les réserves hydriques sont **fortement idéalisés**. Pas de pollinisation, diversité taxonomique, cycle de CO₂/O₂, reproduction sexuée ou compétition explicite pour la lumière.

### Énergie solaire et durée
Le stock solaire initial a été augmenté de `3e14` à `3e16` J afin de permettre de longues simulations écologiques, tout en restant **fini**. Cela n'est ni une réserve astrophysique réaliste ni une preuve de durabilité indéfinie.

### Bilans invariants
```text
Eau totale  = surface + sol + atmosphère (vapeur + nuages) + plantes + animaux
Matière sèche = substrat + biomasse vivante + graines sèches + biomasse/énergie chimique animale équivalente
Énergie = potentiel gravitationnel + chaleur sensible + chaleur latente + énergie solaire restante
          + rayonnement sortant compté + énergie chimique végétale/graines + énergie chimique animale
```
La V2.7 introduit également les données géographiques de pluie, vapeur, nuage, eau végétale, stress et traits génétiques dans l'export CSV.

### Contrôles navigateur (Chromium)
- **Seed 42, réglages par défaut, 8 000 pas :** environ **61 herbivores vivants**, **90 naissances cumulées**, **802 cellules végétalisées** et **470 dispersions de graines cumulées**, avec **22,7 millions de kg d'eau tombés** en précipitations cumulées (cumul des transferts, et non masse nouvelle). Ce scénario montre une persistance à cet horizon, pas un équilibre démontré.
- **1 000 pas :** environ **1,20 million de kg** de pluie cumulée. Présence mesurée de vapeur, nuages et précipitations spatialisées.
- Configurations vérifiées : pluie désactivée (0 kg tombé en 1 300 pas), absence de graines (aucune plante à 900 pas), Soleil nul (aucune plante à 800 pas), forte mutation et 120 herbivores (1 200 pas), rétention nulle (aucune plante à 800 pas). Aucun échec du moteur ni de conservation dans les scénarios.
- Réinitialisation : les mêmes observables après 500 pas sont reproduites **exactement**. Vérification du rendu mobile à 390 px, sans débordement horizontal.
- Les tests sont des **tests d'intégration navigateur du prototype**, pas une calibration scientifique ni des tests du core historique.

**PR empilée sur #25 (V2.6) ; fusionner les PR du plus ancien au plus récent.**
