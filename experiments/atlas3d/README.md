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
