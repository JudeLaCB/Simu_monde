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
