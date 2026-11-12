# Monde VJ — Atlas 3D, couche 01 : Relief

## Démarrage

Ouvre `Monde_VJ_3D_Couche_01_Relief.html` directement dans Chrome ou Edge. Aucun serveur, aucune bibliothèque externe et aucune connexion Internet ne sont nécessaires. Sur les navigateurs compatibles, l'affichage utilise WebGL2 ; sinon une projection 3D sur Canvas 2D prend le relais.

## Contrôles

- Clic gauche + glisser : faire tourner la caméra.
- Molette : zoomer et dézoomer.
- Clic droit + glisser (ou Maj + glisser) : déplacer la cible.
- Clic simple : inspecter une cellule du relief (coordonnées, pente, altitude).
- Boutons « Vue perspective » et « Vue du dessus ».
- Seed, rugosité, profondeur des bassins et trois profils géographiques, comme sur V2.11.
- L'échelle verticale est un **facteur de visualisation** : elle ne modifie pas les valeurs d'altitude exportées en CSV.
- Coloration naturelle, carte d'altitudes ou carte des pentes ; courbes de niveau et grille métrique.
- Export CSV (10000 points) et OBJ (19602 triangles) depuis l'interface. L'OBJ intègre le facteur d'exagération verticale courant.

## Contrat technique

- Terrain de 100 × 100 échantillons espacés de 10 mètres, couvrant 1 km² environ.
- Les fonctions de topographie `hash2`, `noise`, `featureRng`, `pickCenter`, `makeShape`, `generateTerrain`, `buildLandClasses` sont reproduites exactement de V2.11.
- Vérification effectuée : les **10 000 altitudes** et les **10 000 pentes** sont bit à bit identiques à V2.11 avec la seed 42 et les réglages de référence.
- Test navigateur (Chrome/Chromium, rendu Canvas de secours) : réinitialisation déterministe, autre seed produisant un paysage différent, vue du dessus, inspection d'une cellule, exports OBJ/CSV, affichage mobile 390 px sans débordement ni erreur JavaScript.
- **Le chemin WebGL2 est implémenté mais non testé sur une machine dotée d'un GPU fonctionnel**. Son comportement devra être confirmé sur le PC de l'utilisateur.

## Roadmap couche par couche

1. Relief (actuelle) — maillage et inspecteur géographique.
2. Eau — lacs en volumes, écoulement, infiltration, conservation de masse.
3. Atmosphère — température, ensoleillement, vent et nuages 3D.
4. Sol/végétation — croissance, absorption racinaire, transpiration, génomes végétaux.
5. Faune — herbivores et prédateurs dans l'espace tridimensionnel, collisions.
6. Complexité — érosion, sous-sol, économie de calcul et nouvelles lois d'émergence.

Le passage 3D ne recrée pas automatiquement le moteur physique en 3D : chaque couche devra être validée numériquement avant activation. Les anciennes versions 2D ne sont pas modifiées.


## Couche 02 — Eau et infiltration

**Prototype autonome :** [layer02_water.html](layer02_water.html). Fonctionne hors ligne, avec WebGL2 si disponible et une vue 3D Canvas de secours. Le relief de la couche 01 est conservé : **mêmes 10 000 altitudes et 10 000 pentes que Monde VJ V2.11** (seed et paramètres identiques).

### Physique incluse

- Grille identique au prototype V2.11 : **100 × 100 cellules, 10 × 10 m/cellule, monde de 1 km²**.
- `terrain[i]` reste le relief en mètres. `water[i]` mesure la profondeur d'eau libre en mètres au-dessus du relief ; `soilWater[i]` mesure l'eau infiltrée en hauteur équivalente de colonne d'eau, également en mètres.
- Distribution initiale **strictement reprise de V2.11** : poches / sources en altitude / surface déjà de niveau ; la quantité d'eau est un stock global fini, non une génération de lacs préprogrammés.
- Flux d'eau de surface : chaque paire de cellules adjacentes échange en direction du niveau libre le plus bas, selon `surfaceLibre = terrain + profondeurEau`, à débit limité par la profondeur d'eau disponible et la fluidité `0.04–0.42`. Les paires de cellules sont traitées alternativement selon leur ordre de parcours, **comme V2.11**.
- Infiltration locale : `min(eau_surface, capacité_sol - eau_sol, 0.012 m/pas)`, capacité `0.8 m × rétention en %`. Aucun ruissellement souterrain, drainage latéral ou débordement de la carte.
- Conservation de l'eau : `masse_totale = 1000 kg/m³ × 100 m² × Σ(eau_surface + eau_sol)`. **Aucun apport ni perte d'eau** ; cette couche ne simule **pas encore** l'évaporation/condensation/pluie.
- Bilan énergétique fermé **idéalisé** : l'énergie potentielle gravitationnelle perdue par l'écoulement et l'infiltration est accumulée dans un compteur de chaleur dissipée, et non effacée. La température n'est pas encore modélisée en 3D.
- Le facteur d'exagération verticale ne modifie **que l'affichage** et l'OBJ exporté, jamais l'eau ni les échanges entre cellules.

### Interface et observations

- Volume 3D bleu transparent calculé par cellule, surfaces et rebords visibles ; transparence et affichage activables/désactivables.
- Simuler/pause, avancer de 1 ou 100 pas, vitesse 1×, 4×, 12×, retour à l'état initial de l'eau. Boutons de lecture flottants visibles directement dans la carte.
- Affichage des masses en surface et dans le sol, profondeur maximale, superficie humide, débit déplacé et infiltré par pas, erreur relative sur masse et énergie ; inspection d'une cellule sur la carte, mini-carte actualisée.
- CSV : coordonnées, altitude du terrain, profondeur, altitude de la surface libre, eau infiltrée, volumes de surface/sol, pente et type de relief. L'export OBJ concerne le terrain solide uniquement.

### Tests reproductibles

- **Comparaison directe avec V2.11 :** seed 42, morphologie « Massifs et bassins », quantité initiale 30 %, distribution « poches », fluidité 0.22, rétention 60 % ; en désactivant les agents, les végétaux, l'évaporation et la pluie de V2.11, **les 10 000 profondeurs de surface et les 10 000 profondeurs infiltrées restent exactement identiques à l'initialisation et après 1, 50, 200 et 500 pas**. Le relief est également identique, coordonnée par coordonnée.
- Seed 42 par défaut, pas 500 : masse totale **1.85×10⁹ kg** ; environ **1.590×10⁹ kg en surface et 2.597×10⁸ kg dans le sol**, profondeur maximale **10.66 m**, ~45 ha avec plus de 3.5 cm d'eau.
- Après 3000 pas par défaut et 1000–1500 pas sur deux autres morphologies / conditions de rétention et fluidité, les erreurs relatives de masse et énergie restent `<1e-9`, aucune profondeur d'eau négative ni alerte JavaScript.
- Réinitialiser puis simuler 500 pas : profondeurs d'eau de surface et du sol identiques au bit près.
- Test de la lecture depuis les commandes flottantes, réglages, exports CSV/OBJ, vues perspective et dessus, bascule de l'eau, écran mobile 390 px sans débordement.
- WebGL2 / GPU **non vérifié dans l'environnement de test** : le rendu Canvas de secours a été testé et inspecté ; le code WebGL2 est intégré pour navigateurs compatibles.

### Limites et prochaine couche

Il s'agit pour l'instant d'un **champ de hauteurs 2D représenté en 3D**, sans fluide volumique de type Navier–Stokes, pression hydrostatique 3D, vagues hydrodynamiques, érosion, aquifères ni météo. L'eau n'est pas calculée sur des voxels, elle est rendue visuellement comme une surface et des flancs au-dessus des cellules où sa profondeur est positive. Les rivières et lacs ne sont pas des objets placés : ils résultent des hauteurs d'eau et du terrain.

**Couche 03 prévue :** température sol/atmosphère, jour/nuit, évaporation, advection des nuages, pluie et transpiration, en réintroduisant les bilans complets de V2.11.

L'historique Python et les prototypes 2D ne sont pas modifiés. PR empilée sur **#31** (Atlas 3D couche 01).


## Couche 03 — Atmosphère : Soleil, jour/nuit, nuages, vent et pluie

**Prototype autonome :** [layer03_atmosphere.html](layer03_atmosphere.html), à ouvrir dans le navigateur. Le relief 3D (couche 01) et la dynamique d'eau surface/sol (couche 02) restent inchangés. Pas de modification des prototypes précédents ni de `src/`.

### Modèle

- **Jour/nuit** : 1 000 pas par jour, dont 500 éclairés. Température atmosphérique globale, température du sol par cellule, transfert sol-air, diffusion thermique entre cellules et refroidissement radiatif. Réservoir d'énergie solaire **fini** (initialement `3e16 J`), comme dans Monde VJ V2.11.
- **Évaporation** : eau de surface ou de sol, limitée par la température locale et la chaleur disponible ; transferts en vapeur, énergie latente et énergie potentielle gravitationnelle comptabilisés.
- **Nuages et pluie** : deux réservoirs atmosphériques spatialisés de 100×100 cellules, vapeur et nuages liquides. Vent dominant avec advection bilinéaire conservant la masse, condensation et réévaporation dépendant du seuil de saturation, pluie prélevée sur les nuages, réchauffement par condensation et chute gravitationnelle. Relief susceptible de favoriser les précipitations au vent.
- **Vent** : 0–300 %, direction automatique **eau → terre** ou direction manuelle. Forçage géographique simplifié, pas de simulation Navier–Stokes ; bords atmosphériques périodiques, bords hydrologiques fermés.
- **Vue 3D** : nuages représentés en halos aériens projetés selon la caméra, traits de pluie, et mini-carte alternativement relief/eau, nuages, pluie cumulée ou température du sol. La hauteur des nuages est **visuellement comprimée** pour dégager le terrain ; cette compression ne change pas l'altitude physique de référence de l'énergie. Fonctionne hors ligne avec WebGL2 ou en mode de secours Canvas.
- **Inspection et CSV** : profondeur, eau du sol, températures, vapeur, nuages, pluie cumulée par cellule. Export OBJ du terrain conservé.

### Bilans

```text
M_eau = M_surface + M_sol + M_vapeur + M_nuages
E_total = E_gravitationnelle + E_sensible(sol + air) + E_latente(vapeur)
          + E_solaire_restant + E_rayonnement_sortant
```

Pluie et évaporation déplacent l'eau entre réservoirs ; les précipitations cumulées représentent un **transfert** et non de l'eau créée. Le rayonnement émis est compté comme énergie sortie du système atmosphérique, mais reste dans le budget de comptabilité élargi.

### Contrôles Chromium

- **Seed 42, paramètres par défaut, 8 000 pas :** température de l'air **18,2 °C**, pluie cumulée **17,22 millions de kg**, dont **8,04 millions de kg** sur des cellules de terre ; erreur relative eau **1,8×10⁻¹⁵**, énergie **4,8×10⁻¹⁵**.
- **Parité hydrologique stricte avec V2.11** lorsque les animaux, plantes et nouvelles phases atmosphériques sont désactivés : les **10 000 profondeurs de surface et les 10 000 réserves d'eau du sol sont identiques** après 350 pas.
- Reset puis 300 pas : eau de surface et nuages identiques ; évaporation nulle : aucun nuage ni pluie ; pluie désactivée : eau atmosphérique présente sans précipitation ; Soleil nul : réserve solaire inchangée.
- Test bassin côtier, vent est 300 % et 800 pas : pluie non nulle, bilans conservés. Export CSV et affichage mobile 390px validés, sans erreur JavaScript.
- **Rendu 3D Canvas de secours testé visuellement ; chemin WebGL2 non validé**, car l'environnement Chromium ne dispose pas de WebGL2.

### Limites et couche suivante

Ce n'est **pas une atmosphère physiquement volumique** : champs de vapeur et nuages 2D projetés en 3D, température de l'air globale, vent non issu de la dynamique des pressions et précipitations paramétrées. Modèle climatique expérimental non calibré, aucun aquifère, pas d'érosion. **Pas encore de végétation, ni de transpiration des plantes, ni de faune** dans cet Atlas 3D. La couche 04 ajoutera la végétation et reconnectera les échanges eau/matière/énergie.

**PR empilée sur #32 (Atlas 3D couche 02), elle-même empilée sur #31 et sur l'historique des versions 2D.**


## Couche 03b — Relief et transport des nuages par les vents

**Prototype HTML hors ligne :** [layer03b_terrain_wind.html](layer03b_terrain_wind.html). Il reprend **tout** le terrain, l'eau et le cycle météo de la couche 03, en remplaçant le vent uniforme par un **champ horizontal par cellule (10 000 vecteurs)**.

### Règles de vent

- Direction dominante réglable : mode eau→terres, est, ouest, nord ou sud. Intensité 0–300 %.
- Le champ local dépend des altitudes autour de chaque cellule. Une hausse de relief dans la direction du vent ralentit le flux ; le vent se dévie vers le passage latéral plus bas ; un corridor bas peut accélérer le flux ; un versant descendant est identifié comme abrité.
- **Soulèvement au vent** : indice local qui accroît le refroidissement et la pluie en consommant l'eau nuageuse. **Versant sous le vent** : indice d'abri qui réduit ces effets. Les coefficients sont heuristiques.
- Advection **bilinéaire avant et conservative**, différente pour chaque cellule, avec poids positifs et somme des poids égale à un. Les masses vapeur et nuages sont redistribuées, jamais créées. Le transport atmosphérique garde les frontières périodiques.
- Le curseur « Influence du relief sur le vent » est réglable de 0 à 200 % (130 % par défaut). À 0 %, les vecteurs locaux coïncident avec le vent dominant uniforme. Cela permet une comparaison contrôlée dans **cette même version 03b**.
- Nouvelles mini-cartes : **Champ de vent** (flèches), **Soulèvement / abri** ; inspection du vent local, indice de soulèvement et de protection ; colonnes ajoutées au CSV. Les nuages restent visualisés en 3D au-dessus du terrain.

### Contrôles Chromium

- Seed 42, paramètres défaut, **4 000 pas** :
  - Influence du relief **0 %** : **46,3 %** des précipitations sur les terres, 0° de déviation par rapport au vent uniforme.
  - Influence du relief **130 %** : **81,5 %** des précipitations sur les terres, déviation locale maximale **43,2°**.
  - Influence du relief **200 %** : **84,1 %** sur les terres, déviation maximale **55,3°**.
  - L'indicateur « terre » distingue les cellules avec moins de 5 cm d'eau libre **au moment où il pleut**, et non une classe de biomes fixée.
- Bilan total d'eau et énergie, erreurs relatives numériques inférieures à 1e-13 dans ces scénarios.
- Test seed 517, relief « Chaînes et vallées », vent 300 %, relief 200 %, **2 300 pas**, réservoirs non négatifs et erreurs relatives inférieures à 1e-9.
- **Répétabilité exacte** après reset + 250 pas ; désactivation totale du vent ⇒ tous les vecteurs nuls.
- **Hydrologie identique à la couche 03** lorsque évaporation et pluie sont coupées : même terrain, 10 000 hauteurs d'eau de surface et 10 000 réserves d'eau du sol après 600 pas.
- Affichage mobile 390 px sans débordement ; test du fallback Canvas. **Rendu GPU WebGL2 non validé** dans l'environnement de tests.

### Limites

Le champ de vitesse est **horizontal et dépend du relief**, pas un solveur d'air volumique 3D. L'indice de soulèvement ne correspond pas à un calcul explicite de vitesse verticale ni à une pression atmosphérique. Le vent dominant et son énergie cinétique sont des forçages externes non inclus dans les bilans mécaniques. Les déviations et la pluie orographique ne sont **pas calibrées météorologiquement**. Pas de tourbillons turbulents résolus, couches d'altitude, fronts ni Navier–Stokes ; bords atmosphériques périodiques. La conservation comptable de l'eau et de l'énergie de la couche 03 demeure.

La version est archivée séparément ; **aucune modification des versions précédentes ni du moteur Python historique**. PR empilée sur #33.


## Couche 04 — Végétation et arbres 3D

**Prototype HTML autonome :** [layer04_vegetation_trees.html](layer04_vegetation_trees.html). Bâti sur la couche 03b (vents orographiques). Terrain, hydrologie, jour/nuit, nuages et pluie sont préservés ; les autres prototypes HTML et le cœur Python ne sont pas modifiés.

### Biologie et ressources (modèle expérimental)

- Conditions initiales : graines dormantes distribuées par seed (60 % par défaut), prélevées sur **un stock local fini de matière sèche** (38 à 100 kg/cellule). Chaque graine contient 4 g de matière sèche et de l'énergie chimique correspondante.
- Germination après **160 pas de sol suffisamment humide et stable** (réglable 40–500), si la température, la pente et la profondeur d'eau sont favorables. Une plante adulte n'est plus conditionnée à ce compteur de stabilité ; elle dispose d'une résistance à la sécheresse et peut dépérir si le stress persiste.
- Photosynthèse idéalisée : prélèvement de matière du substrat vers la biomasse, financé par une fraction finie de l'énergie solaire reçue. Mort : transfert de la matière végétale vers le substrat et de l'énergie chimique en chaleur. **Le modèle ne calcule pas la véritable fixation du CO₂.**
- Racines : retrait de l'eau du sol vers l'eau corporelle de la plante ; transpiration vers le champ local de vapeur avec consommation de chaleur latente et paiement de l'énergie potentielle de la vapeur. La pluie retourne dans les lacs et sols selon la physique atmosphérique de la couche 03b.
- Une plante porte cinq traits héréditaires (résistance à la sécheresse, consommation d'eau, tolérance thermique, taux de croissance, silhouette de feuillage). Les plantes suffisamment développées peuvent disperser des graines vers les cellules voisines, avec des mutations paramétrables. Les graines coûtent réellement 4 g de biomasse au parent.
- Pas encore de carbone/oxygène explicites, de saisons, de compétition radiative inter-arbres, de reproduction sexuée, de diversité d'espèces ou de faune en 3D.

### Rendu 3D procédural

- Un arbre par cellule au maximum ; **tronc cylindrique effilé**, branches et **couronnes feuillues lobées en volumes** ou **conifères étagés**. L'âge géométrique (hauteur et couronne) découle de la biomasse ; les arbres ne sont pas pré-positionnés.
- Géométrie triangulaire colorée et éclairée en WebGL2 ; moteur de secours Canvas avec projection des arbres selon la caméra. Le rendu logiciel est testé ; **le chemin WebGL2/GPU n'a pas pu être exécuté dans notre navigateur de test** (indisponible dans l'environnement).
- Densité de rendu (65 % par défaut) et facteur de taille visuelle (2,2× par défaut) indépendants des stocks physiques. Un plafond de 1 500 arbres dessinés limite l'utilisation du GPU mais ne limite **pas** le nombre de plantes simulées.
- Le bouton **🌳 + 1 000 pas** permet d'observer les premiers arbres sans plusieurs dizaines de clics. Les arbres sont absents du terrain initial : seules les graines sont présentes.
- Mini-cartes **Végétation** et **Humidité du sol**, télémetrie biomasse, eau racinaire, graines, mutations, stress et bilans, inspection d'une cellule. CSV complet par cellule, export OBJ du relief inchangé.

### Bilans et tests Chromium

```text
M_eau = surface + sol + vapeur + nuages + eau des plantes
M_sèche = substrat + graines + biomasse végétale
E_totale = E_gravitationnelle + E_sensible + E_latente + E_solaire_restante
            + E_rayonnement_comptabilisé + E_chimique_plantes
```

- Seed 42, paramètres par défaut : à **250 pas : 528 cellules végétalisées**, à **600 : 908**, à **1 100 : 972**, à **2 300 : 1 187** ; dont **640 arbres visibles** au pas 2 300 avec densité graphique 65 %.
- À 2 300 pas : biomasse végétale ~**18 503 kg**, erreur relative de conservation eau, masse sèche et énergie **~10⁻¹⁵**.
- **Sans graines (densité 0 %), parité exacte au bit près** avec la couche 03b pour les 10 000 valeurs de surface, sol, vapeur, nuages après 300 pas ; même énergie totale.
- Réinitialisation après 400 pas : reproductibilité des états et compteurs biologiques ; sans Soleil ou avec rétention 0 %, aucune pousse.
- Test seed 517 / relief montagneux / vent 300 % / mutation 100 % / croissance 200 % sur 1 200 pas : bilans conservés. CSV : 10 000 lignes de données vérifiées ; rendu de secours et écran mobile 390 px sans débordement.
- Les paramètres de croissance, stocks biologiques et formes d'arbres sont **idéalisés** ; il ne s'agit pas d'une prédiction écologique ni d'une représentation volumique des réactions chimiques.

**Prochaine étape :** observer les peuplements 3D et leur répartition selon l'humidité, puis envisager les herbivores de V2.11 projetés sur ce terrain (couche 05). PR empilée sur #34.


## Couche 04b — Tous les arbres visibles (sans réduction biologique)

**Prototype :** [layer04b_all_trees_lod.html](layer04b_all_trees_lod.html). Les mêmes lois d'eau, d'énergie, de photosynthèse, de génétique et de croissance que la couche 04 sont conservées.

### Modification graphique

- **100 % des arbres par défaut**, au lieu de 65 %. Toute cellule contenant un arbre vivant (biomasse >0,025 kg, seuil du compteur écologique) reçoit sa propre géométrie dans la scène, y compris en sol temporairement inondé.
- **Suppression du plafond graphique de 1 500 arbres** : le monde comporte au maximum 10 000 cellules, avec au plus un arbre par cellule.
- L'option **Auto / LOD adaptatif** simplifie la géométrie des arbres lointains pour économiser les triangles sans supprimer aucun individu. Rafraîchissement après modification de la caméra et mise à jour progressive lors de la croissance.
- L'option **Détaillé partout** reproduit les couronnes et branches complètes même au loin ; plus coûteuse pour le processeur, la mémoire GPU et la fréquence d'images.
- Le rendu Canvas de secours conserve toutes les silhouettes et simplifie les arbres éloignés. La densité 10–100 % reste un **réglage graphique optionnel**, pas une modification de la simulation.
- Compteur de triangles en mode WebGL2, comptage indépendant des arbres affichés.

### Tests Chromium

- Seed 42, **2 300 pas** : 1 187 cellules portant des arbres et **1 187 arbres dessinables** ; version 04 précédente : **640 arbres** sur les mêmes 1 187 cellules.
- Curseur 30 % : 348 arbres, puis retour 100 % : 1 187 ; mode détaillé : nombre d'arbres inchangé.
- **5 600 pas** : 1 319 cellules portant des arbres / **1 319 arbres** dans la version 04b, avec affichage mobile 390 px sans débordement ni exception JS.
- Avec les mêmes paramètres, la biomasse, l'eau, la masse sèche et l'énergie de la couche 04 sont numériquement **identiques** à 2 300 pas. Erreurs relatives de conservation autour de 10⁻¹⁵.
- Le rendu de secours Canvas a été testé. **WebGL2/GPU reste non vérifié dans l'environnement Chromium de test**, qui ne l'expose pas. La présence de 32 Go de RAM ne garantit pas une fluidité élevée : les performances dépendent aussi du GPU, du nombre de triangles et du coût de mise à jour des meshes.

**PR empilée sur #35 (Atlas 3D couche 04).** Aucun autre fichier de prototype ni le moteur Python ne sont modifiés.


## Couche 05 — Herbivores quadrupèdes 3D (introduction au pas 2 000)

**Prototype HTML autonome :** [layer05_herbivores_3d.html](layer05_herbivores_3d.html). Basé sur la couche 04b (affichage des arbres à 100 %) et compatible avec la suite du simulateur sans modifier les versions précédentes ni `src/`.

### Introduction de la faune

- **Aucun animal au pas 0…1 999.** Au **pas 2 000 exactement**, après les deux premiers cycles de 1 000 pas de végétation et de climat, une population initiale de **50 herbivores par défaut** (0–150 réglable) est tirée dans les **cellules réellement habitables** : terrain accessible, eau libre peu profonde, pente faible, végétation vivante et ressources suffisantes.
- Cette apparition est **unique** : aucun repeuplement artificiel si les individus meurent ; le reste de la dynamique vient uniquement des naissances et des décès. Si aucun habitat convenable, aucun individu n'est créé. La date 2 000 est un **délai conventionnel**, non une démonstration d'équilibre écologique.
- Les animaux sont fabriqués à partir d'**eau et de substrat pris sur leur cellule locale**. L'énergie chimique initiale est équilibrée en retranchant le surplus de chaleur comptabilisé. Les autres réservoirs conservent leurs stocks initiaux.
- Bouton **« ⏩ Atteindre le pas 2 000 »** : simulation par blocs avec retour de contrôle au navigateur, indicateur de progression et annulation au reset. Bouton **« Suivre un herbivore »**, sélection d'un individu dans la vue, caméra poursuivant ses mouvements.

### Cerveaux, physiologie et rendu 3D

- Réseau neuronal héréditaire repris de Monde VJ **V2.11** (17 entrées, 19 neurones cachés, 2 sorties), avec prédisposition de **recherche alimentaire 70 %** et mutations des descendants **14 %**, réglables. Sans prédateur dans cette couche, les signaux de menace restent nuls.
- Chaque individu : position continue dans le plan horizontal, orientation, hauteur interpolée sur le terrain, énergie, eau, matière sèche structurelle, âge, génération, gènes. Localement : pâturage sur la biomasse végétale, abreuvement dans les eaux peu profondes, pertes de matière/énergie/urine vers les sols, vieillissement, mort, reproduction avec partage des réserves et mutations.
- **Quadrupède polygonal 3D** construit entièrement en JavaScript : torse, tête, cou, oreilles, museau, queue, quatre pattes avec articulations de marche, sabots et variations de couleur entre générations. Géométrie reconstruite selon la position/orientation et la phase de pas, dessinée en **WebGL2** ; fallback Canvas par projection de parties articulées.
- **Taille d'affichage** réglable de 1× à 6×, **3× par défaut** pour rendre les petits animaux discernables dans une forêt de 1 km². Cette échelle est purement visuelle, sans effet biologique.
- **Tous les individus sont représentés** sans filtrage graphique, limite biologique/technique de **150 herbivores**. Position des animaux sur la mini-carte, inspections individuelle et par cellule, CSV individu et CSV environnement enrichi du nombre d'animaux par cellule.

### Comptabilité conservée

```text
M_eau = eau_surface + eau_sol + vapeur + nuages + eau_plantes + eau_animaux
M_sèche = substrat + graines + biomasse_plantes + structure_animaux + énergie_animaux / 18 MJ/kg
E_totale = gravité + chaleur sensible + chaleur latente + Soleil restant
          + rayonnement sorti comptabilisé + énergie chimique plantes + énergie chimique animaux
```

Les mécanismes sont **idéalisés** : par exemple, la nutrition ne représente pas une digestion chimique réaliste, et la conversion d'énergie à l'introduction est un choix de comptabilité fermé.

### Contrôles Chromium

- **Seed 42, pas 1 999** : 0 individu, **identité stricte** des 10 000 valeurs de chacun des huit champs eau libre, eau du sol, vapeur, nuages, biomasse végétale, substrat, graines et eau végétale avec la couche 04b ; même total d'énergie.
- **Pas 2 000** : 50 individus exactement ; erreurs relatives de bilan eau **1,8×10⁻¹⁵**, matière sèche **2,2×10⁻¹⁵**, énergie **1,2×10⁻¹⁵**.
- **Pas 2 500 : 50 vivants**. **Pas 6 000 : 150 vivants**, 163 naissances et 63 décès cumulés ; bilans respectés avec erreurs relatives **< 10⁻¹⁴**, aucune alerte moteur. Le plafond 150 n'est pas un équilibre naturel.
- Contrôle de la commande d'introduction asynchrone sur écran mobile 390 px : progression jusqu'à 2 000, 50 animaux, pas de débordement horizontal ; caméra de suivi et état individuel fonctionnels.
- **WebGL2/GPU non testé** dans l'environnement de test, même en mode SwiftShader. Le fallback Canvas a été visualisé ; vérifier le moteur polygonal WebGL2 dans le navigateur local avec GPU activé.

### Limites et étapes futures

La physique reste une simulation **2.5D** sur grille de terrain, représentée avec des corps en 3D. Il manque la collision géométrique avec les troncs, la consommation de feuilles par hauteur, les sources de nourriture distinctes (herbe/arbres), l'apprentissage neuronal individuel et les prédateurs 3D. La prédation ne doit donc pas encore être évaluée. Le choix du pas 2 000 ne garantit pas que les conditions écologiques sont stables.

**PR empilée sur #36 (couche 04b), puis #35, #34, #33, #32, #31.**


## Couche 06 — Carnivores 3D et chaîne trophique

**Prototype :** [layer06_carnivores_3d.html](layer06_carnivores_3d.html). Aucune modification des couches 01–05 ou du moteur Python. Herbivores introduits **une fois au pas 2 000** ; carnivores **une fois au pas 3 000**, sans repeuplement automatique.

# Monde VJ — Atlas 3D / Couche 06 : carnivores

## Lancer

Ouvrir `Monde_VJ_Atlas_3D_Couche_06_Carnivores.html` avec Chrome ou Edge. Ce fichier est **autonome** et fonctionne **hors ligne**. Pas de dépendance CDN ou de serveur à installer.

Utiliser « Atteindre le pas 3 000 » pour calculer les premiers jours : herbivores à **2 000 pas**, carnivores à **3 000 pas**, en une introduction initiale unique. Le bouton « Suivre un carnivore » permet de rapprocher la caméra de l'animal. La mini-carte, les compteurs et les exports CSV séparent les deux populations.

## Mécanismes ajoutés

- Carnivores en coordonnées continues 2D sur terrain 3D (altitude interpolée) : corps polygonal allongé, tête, museau, oreilles, queue et quatre pattes articulées en WebGL2, projection Canvas de secours.
- Un réseau neuronal propre à chaque carnivore (**12 entrées, 8 neurones cachés, 2 sorties, 122 coefficients**) commande direction et vitesse à partir des signaux gauche/devant/droite de présence de proies, eau, obstacles et besoins internes. **Instinct initial 90 %** par défaut, réglable de 0 à 100 % : prédispositions codées dans les poids initiaux, puis hérédité avec mutation. **Pas d'apprentissage au cours de la vie** et pas de suivi scripté de la proie la plus proche.
- Détection jusqu'à 155 mètres ; vitesse jusqu'à 10,3 m/pas. Capture seulement à distance <5,4 mètres **et dans un cône frontal** (0,80 rad par rapport à la tête), puis période de digestion de 250 pas pendant laquelle aucune nouvelle prise n'est possible. La réussite au contact frontal reste **déterministe**, et non un combat probabiliste.
- Eau, matière sèche et énergie de la proie transférées à son prédateur ou aux réservoirs du sol et de chaleur. Métabolisme, déplacement, eau corporelle, reproduction, mort et déchets respectent la comptabilité de masse et d'énergie idéalisée.
- L'instinct de fuite herbivore est fonctionnel en présence de carnivores et l'endurance diminue pendant le sprint. Le curseur « Instinct neuronal de fuite » est disponible. Les arbres continuent de s'afficher à 100 %.
- Population initiale configurable **0–30** (4 par défaut), plafond technique biologique de **55 carnivores**, plafond de **150 herbivores** hérité de la couche précédente. Les deux plafonds sont des limites de calcul, **pas un mécanisme d'équilibre écologique naturel**.

## Tests Chromium (rendu logiciel)

Seed 42 :

| Pas | Herbivores | Carnivores | Captures cumulées |
|---:|---:|---:|---:|
| 1 999 | 0 | 0 | 0 |
| 2 000 | 50 | 0 | 0 |
| 2 999 | 71 | 0 | 0 |
| 3 000 | 71 | 4 | 0 |
| 5 000 | 150 | 8 | 17 |
| 7 000 | 150 | 11 | 35 |
| 9 000 | 150 | 18 | 62 |
| 11 000 | 150 | 23 | 102 |

Seed 517 : pas 3 000 : 65 herbivores et 4 carnivores ; pas 5 000 : 107 et 7 (17 captures) ; pas 6 500 : 150 et 10 (29 captures). Pas d'erreur JS, de masse négative ni d'alerte de conservation ; écarts relatifs d'eau, matière sèche et énergie de l'ordre de 10^-15 à 10^-14 dans les scénarios testés.

- **Témoin 0 carnivore, seed 42, 4 300 pas : identité bit-à-bit** avec la couche 05 pour les herbivores et leurs gènes, eau libre/sol, vapeur/nuages, végétation/graines/substrat et comptabilité énergétique.
- **Réinitialisation 3 400 pas** : les états complets des carnivores et herbivores, génomes inclus, ainsi que les bilans sont reproduits exactement.
- Mobile **390 px** : aucun débordement horizontal, simulation et suivi fonctionnels.
- Le navigateur de test n'expose pas WebGL2, même en tentant SwiftShader. **Le rendu Canvas de secours a été examiné**, mais **la géométrie WebGL2/GPU 3D n'a pas encore été validée sur un PC équipé**.

## Ce que ce modèle ne prouve pas

La cohabitation constatée sur ces deux seeds et ces durées **n'est pas** une preuve de stabilité écologique. Il faut tester davantage de seeds, périodes longues et scénarios de ressources ; le plafond de 150 herbivores altère les dynamiques. Les réseaux commencent avec des comportements prédisposés : aucune intelligence de chasse n'a spontanément émergé sans règles initiales. La physique reste une carte à hauteurs (2.5D), sans collision volumique avec les troncs, fluides 3D résolus, combat probabiliste ou chaîne de décomposition différée.

Le code de la couche 05 et les versions précédentes sont conservés.

La PR de la couche 06 est empilée sur la PR #37 (herbivores 3D), elle-même empilée sur #36 et toutes les couches précédentes. Le prototype est un modèle 2.5D à rendu 3D, pas une simulation de locomotion volumique ou un modèle zoologique calibré.
