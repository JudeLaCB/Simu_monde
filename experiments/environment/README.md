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


## V2.8 — Vent dominant, pluie continentale et correction de la surchauffe

[Ouvrir le prototype V2.8](v2_8_vent_pluie_terres.html) — laboratoire HTML autonome ; l'ancien moteur Python et V2.7 restent inchangés.

### Diagnostic confirmé par tests navigateur

- V2.7 seed 42 à **8 000 pas** : atmosphère `61,5 °C`, température moyenne du sol `60,3 °C`. Les végétaux ne tolèrent pas ces températures. Environ **14 %** des précipitations cumulées tombent sur des cellules de terre avec moins de 5 cm d'eau ; le reste tombe sur l'eau de surface.
- **V2.8, même seed et paramètres par défaut :** à 8 000 pas, atmosphère `18,1 °C`, sol moyen `20,8 °C`, **1 363 cellules végétalisées** et **125 herbivores vivants**. Aucun équilibre à durée infinie n'est démontré.
- **Expérience contrôlée V2.8 à 4 000 pas :** vent à 0 % => **12,7 %** des pluies sur les terres ; vent automatique à 180 % => **47,9 %** des pluies sur les terres. Cette comparaison isole l'effet du vent **dans la même V2.8**.

### Changements V2.8

1. **Vent persistant et plus rapide :** force réglable 0–300 % ; direction automatique depuis les zones d'eau et bas-relief vers les terres plus hautes, ou direction manuelle est/ouest/nord/sud. Petite modulation de rafales et d'orientation, sans rotation lente inversant les masses d'air. Le vent n'ajoute ni eau ni énergie de mouvement comptable (forçage externe idéalisé).
2. **Transport atmosphérique conservatif :** l'advection avant redistribue les masses de vapeur et de nuages entre quatre cellules par interpolation bilinéaire, même avec déplacements supérieurs à une cellule/pas. Les bords atmosphériques sont **périodiques**. La grille et les réservoirs de surface sont inchangés.
3. **Soulèvement du relief :** une augmentation d'altitude dans la direction du vent augmente le refroidissement et favorise condensation/précipitation. Pluie moins rapide et seuil nuageux accru pour laisser les nuages voyager avant de précipiter. Aucune pluie créée sans eau nuageuse.
4. **Bilan thermique :** coefficient radiatif de l'atmosphère `AIR_COOL_J_K_STEP` relevé de `1.0e8` à `6.5e8 J/K/pas` pour corriger la hausse excessive des températures ; l'énergie rayonnée reste dans le réservoir de rayonnement sortant comptabilisé. C'est un **paramétrage expérimental**, pas une calibration climatique.
5. **Observation :** nouvelles vues « Pluie cumulée » (palette **relative** à la gamme minimum–maximum affichée), précipitation sur terre/eau cumulée, direction/intensité du vent et données CSV `rain_accumulated_kg` ; les cartes « Nuages » ont un meilleur contraste.

### Tests de non-régression

Dans Chromium sur fichier HTML autonome : valeur de la seed 42, 11 000 pas continus sans erreur, et scénario 8 000 pas ; pas d'écart relatif significatif eau, matière sèche et énergie (~1e-14 ou mieux). Réinitialisation + 500 pas = états numériques identiques. Vent à 0 %, vent est à 300 %, pluie à 0 %, seed 517, rendu mobile 390px sans débordement ; aucun avertissement moteur.

### Limites du laboratoire

La vitesse du vent est exprimée en **mètres par pas** (10 m par cellule et 1 000 pas/jour) ; ce n'est ni une dynamique Navier–Stokes ni un vent calibré en m/s. Le mode automatique est un **forçage géographique heuristique** vers les terres, pas un champ de pression météorologique émergent. Les bords périodiques peuvent faire traverser plusieurs fois le monde de 1 km aux mêmes nuages. Une atmosphère 3D, des vents thermiques locaux, les fronts, les pluies au vent/sous le vent, le cycle carbone complet, la croissance végétale à très long terme et l'équilibre écologique sont des développements ultérieurs.


## V2.9 — Prédateurs neuronaux et réseau trophique

**Prototype autonome :** [v2_9_predateurs.html](v2_9_predateurs.html) ; reprend V2.8 sans modification des versions archivées ni du core Python.

### Agents et interactions

- Population initiale : **4 prédateurs par défaut**, réglage 0–40 ; conditions initiales échantillonnées autour des habitats des herbivores lorsque ceux-ci existent.
- Prédateurs mobiles en coordonnées continues (mètres), chacun avec eau corporelle, matière sèche structurelle, énergie chimique, âge, génération et **122 coefficients** constituant son réseau 12→8→2 : capteurs locaux de proies directionnelles (gauche/avant/droite), d'eau, d'obstacles et de faim/soif ; sorties rotation/vitesse. Réseau initial aléatoire déterministe par seed et hérédité avec mutations.
- **Aucune instruction de navigation vers une proie** ; capture seulement si un prédateur arrive à **moins de 8 m** d'un herbivore et a besoin de nourriture. Le réflexe de capture au contact est prédéfini, contrairement à la stratégie de déplacement.
- Les herbivores perçoivent la présence de prédateurs comme un signal de menace incorporé à leurs entrées d'obstacles, mais aucun algorithme de fuite automatique n'est ajouté.
- L'ingestion redistribue l'intégralité des stocks de la proie : matière sèche / énergie chimique vers le prédateur ; excédents vers substrat et chaleur ; eau vers le prédateur et le sol. Les pertes métaboliques retournent au sol. Reproduction et mort ne créent ni matière ni énergie.
- Une naissance répartit les réserves corporelles du parent et transmet le génome avec mutation ; cap technique de 55 prédateurs, en supplément des 150 herbivores.
- **Tableau « Évolution des populations »** avec deux échelles graphiques identifiées, mise à jour toutes les 25 itérations, vue « Prédateurs », compteurs de captures, naissances et morts, export CSV avec nombre de prédateurs par cellule.

### Bilans comptables étendus

```text
Eau totale = eau de surface + sol + atmosphère + végétation + corps herbivores + corps prédateurs
Masse sèche = substrat + graines + plantes + matière sèche herbivores + matière sèche prédateurs
Énergie totale = énergie physique V2.8 + énergie chimique des herbivores + énergie chimique des prédateurs
```

Les rapports structurent une **comptabilité de matière/énergie idéalisée** : pas de chimie physiologique détaillée, pas de carcasse ou décomposition différée, pas d'apprentissage au cours de la vie.

### Contrôles Chromium

- **Seed 42 et paramètres par défaut : à 2 600 pas, 6 prédateurs vivants, 3 naissances cumulées, 7 herbivores capturés, 5 herbivores survivants ; aucune alerte de bilan.** C'est un exemple expérimental et non un équilibre écologique garantissant la survie des deux populations.
- Avec **zéro prédateur**, les variables de V2.8 (eau, température, végétation, énergie, évolution des herbivores) sont **identiques au bit près** à 600 pas pour les observables comparées.
- Réinitialisation et seconde exécution de 2 400 pas : état et génomes des prédateurs identiques.
- **0 herbivore, 10 prédateurs : zéro capture après 1 400 pas**.
- **120 herbivores et 40 prédateurs :** 1 400 pas sans alerte de bilan ou dépassement du cap, en dépit d'une très forte prédation.
- Vérification du rendu mobile à 390px, sans débordement horizontal.
- Conservation numérique eau / matière sèche / énergie, erreurs relatives inférieures à 1e-9 dans les scénarios testés.

### Limites et étude ultérieure

Les réseaux commencent avec des poids aléatoires, les stratégies de chasse efficaces ne sont ni prescrites ni garanties. Des extinctions de prédateurs peuvent survenir lorsque les proies deviennent rares, et une très forte densité peut provoquer la disparition locale des herbivores. La sélection naturelle sur plusieurs générations et une coévolution stable restent à établir empiriquement ; les populations initiales et taux métaboliques sont des paramètres expérimentaux, non une calibration zoologique.

**PR empilée sur #27 (V2.8). Fusionner #22 → #23 → #24 → #25 → #26 → #27 → V2.9.**

## V2.10 — Vision et instinct de chasse héréditaire

Prototype HTML autonome : [v2_10_chasse_instinct_neuronal.html](v2_10_chasse_instinct_neuronal.html).

# Monde VJ V2.10 — Vision et instinct de chasse

Ouvrir `Monde_VJ_V2_10_Vision_Chasse.html` avec Chrome ou Edge. Pas d'installation nécessaire.

## Nouveautés

- Les prédateurs détectent les proies à 155 m dans des directions gauche, devant, droite avec des signaux progressifs (distance et angle).
- Le réseau neuronal 12→8→2 conserve la décision du mouvement, mais les premiers prédateurs héritent d'un instinct neuronal de poursuite. Celui-ci est une hypothèse biologique **explicitement codée**, pas une émergence spontanée.
- Curseur « Instinct neuronal de chasse » de 0 à 100 % (90 % par défaut) : génomes initiaux aléatoires à 0 %, biais neuronal vers les proies à intensité croissante ; tous les coefficients peuvent muter à la reproduction.
- Rotation plus rapide (jusqu'à 0,34 rad/pas). Capture au contact uniquement, à moins de 8 m, et seulement si le prédateur a besoin de nourriture.
- Bouton « Voir la vision » et clic sur un triangle de prédateur pour voir le cône de perception, les proies perçues et leur nombre.

## Expérience comparée

Seed 42, 50 herbivores et 4 prédateurs au départ :
- V2.9 : 6 captures cumulées après 500 pas.
- V2.10 avec instinct 90 % : 16 captures cumulées après 500 pas.

Test isolé : proie à gauche → rotation -0,320 rad/pas ; proie à droite → +0,329 rad/pas.

Après 4 600 pas : 18 captures, 12 herbivores et 2 prédateurs vivants dans le scénario testé. Ces résultats ne prouvent ni stabilité écologique ni apprentissage individuel.

### Conservation et limites

Tests navigateur Chromium : invariants numériques de masse d'eau, matière sèche et énergie (erreur relative de l'ordre de 1e-15), scénario zéro prédateur identique à V2.9 sur les grandeurs comparées à 400 pas, mobile 390 px sans débordement. Les capteurs ne considèrent pas encore l'occlusion par les obstacles, le relief ou la nuit. Seule l'évolution générationnelle (mutations + sélection) peut modifier les connexions ; aucun apprentissage du vivant n'est encore simulé.

**Limite importante :** ce nouvel instinct est volontairement initialisé dans les poids neuronaux. Une capture plus fréquente ne constitue pas une preuve d'intelligence émergente ou d'équilibre proies-prédateurs. La vision ignore encore les occultations par les obstacles et n'est pas affectée par la nuit. La reproduction permet des variations génétiques, sans apprentissage au cours de la vie.


## V2.11 — Coévolution expérimentale : fuite, nutrition et prédation

Prototype HTML autonome : [v2_11_fuite_alimentation_predation.html](v2_11_fuite_alimentation_predation.html) — les versions précédentes et `src/` ne sont pas modifiés.

### Diagnostic de V2.10

- Les prédateurs ont un instinct de poursuite et étaient plus rapides (8,8 m/pas) que les herbivores (5,2 m/pas) ; toute proie à moins de 8 m pouvait être capturée sans lutte, orientation d'attaque ou délai digestif.
- Les herbivores percevaient une menace sans connexion de fuite garantie. Leur réseau de recherche alimentaire commençait également aléatoire.
- **Témoin sans prédateur :** à seed 42, la population peut tomber à environ 9 individus au pas 3 000. La prédation aggrave donc une fragilité nutritionnelle/hydrique préexistante.

### Changements

- **Herbivores :** cinq capteurs de menace couvrant 360° jusqu'à 135 m alimentent cinq canaux neuronaux héréditaires. Instinct de fuite réglable **0–100 %** (75 % par défaut), vitesse de sprint modulée par le danger et par la fatigue qui récupère hors menace. Une fuite augmente le coût énergétique du déplacement ; aucun « aller au refuge » n'est programmé.
- **Alimentation :** six neurones supplémentaires relient signaux locaux de végétation et d'eau aux moteurs rotation/vitesse. Instinct de recherche de ressources réglable **0–100 %** (70 % par défaut). **Ce sont des prédispositions génétiques introduites volontairement, pas des comportements apparus spontanément ; leurs connexions sont mutables et héréditaires.**
- Les 122 anciens poids herbivores sont préservés dans le nouveau réseau étendu ; quand les deux instincts valent 0 %, le comportement d'origine peut être reproduit.
- **Prédateurs :** 10,3 m/pas au maximum et dépense de mouvement de 70 J/m ; attaque seulement à moins de **5,4 m** dans le secteur frontal (angle de 0,8 rad), suivie de **220 pas de digestion/manipulation** sans nouvelle capture. Métabolisme de 950 J/pas. Les premières positions sont à 45–105 m d'un herbivore plutôt qu'à 11–49 m, pour éviter une capture immédiate.
- La reproduction des prédateurs exige désormais >1 300 pas d'âge et >1 700 pas depuis la précédente, avec des réserves suffisantes (>83 % de l'énergie maximale). Aucune population ou nombre de captures n'est fixé artificiellement.
- Graphique de population hérité, nouveau compteur d'herbivores en fuite, vue de vision des prédateurs conservée.

### Mesures de contrôle (Chromium, seed 42, réglages par défaut)

| Pas | Herbivores vivants | Prédateurs vivants | Captures cumulées |
|---:|---:|---:|---:|
| 3 000 | 38 | 8 | 17 |
| 6 000 | 66 | 4 | 19 |
| 9 000 | 150 | 4 | 28 |

À 9 000 pas, **150 est le plafond technique navigateur** des herbivores, pas une preuve d'équilibre naturel. Sur une autre seed (517), la population prédatrice peut au contraire s'éteindre : aucune garantie de coexistence durable.

### Tests

- Sans prédateur, et avec fuite=0 / alimentation=0 : V2.11 reproduit exactement les grandeurs physiques, thermiques, végétales et animales comparées à V2.10 après 700 pas.
- Reset après 1 800 pas et répétition : reproduction identique des grandeurs contrôlées.
- Scénarios longs : eau totale, matière sèche et énergie conservées numériquement, écarts relatifs de l'ordre de 10⁻¹⁴ ou inférieurs ; pas d'alerte moteur sur les scénarios de référence ; pas de débordement mobile à 390px.
- **Limites :** instincts construits et non appris, pas de combat probabiliste ou d'occlusion visuelle, carbone et thermodynamique simplifiés, nourriture/efficacité de chasse stylisées, cap des populations technique. L'équilibre écologique entre espèces reste **une hypothèse à tester sur plusieurs seeds et à très long terme**.

Cette PR est empilée sur #29. Fusionner #22 → #23 → #24 → #25 → #26 → #27 → #28 → #29 → V2.11.
