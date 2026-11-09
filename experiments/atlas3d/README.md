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
