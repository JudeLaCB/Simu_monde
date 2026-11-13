# Monde VJ — Couche 20 · Six niveaux atmosphériques

Ouvrir le [prototype HTML](Monde_VJ_Atlas_3D_Couche_20_Strates_Atmospheriques.html) dans Chrome ou Edge, hors ligne et sans dépendance.

## Usage
- Choisir un des sept paysages et un des sept climats ; **Random Seed** reste disponible. Cliquer sur **Générer**.
- Dans le panneau droit, la **coupe atmosphérique** indique la vapeur et les nuages par couche, les températures et pressions diagnostiques et la vitesse du vent.
- Cliquer sur une cellule du paysage pour consulter sa colonne atmosphérique ; sinon colonne centrale.
- Les paramètres avancés historiques sont préservés et repliés.

## Fonctionnalités
Six tranches au-dessus du sol local : 0–50, 50–200, 200–500, 500–1 000, 1 000–2 000, 2 000–4 000 m. Cela représente **240 000 cellules atmosphériques** sur une grille horizontale de 200×200.

Les réservoirs de vapeur et de nuages sont physiquement ventilés entre les tranches. L'évapotranspiration arrive dans la couche de surface. Le mélange vertical est conservatif, l'advection horizontale (période de 8 pas) utilise des vents cisaillés avec dépôt bilinéaire conservatif. Chaque étage peut condenser, réévaporer et précipiter de l'eau. Les stocks sont réagrégés sans duplication vers les modules historiques. Les bilans incluent une correction d'énergie potentielle de l'eau aux différentes altitudes.

## Ce qui reste simplifié
Les températures et la pression verticale **ne sont pas encore des champs dynamiques résolus** : elles sont déduites d'un gradient et de corrections jour/nuit. Le moteur garde un réservoir global `airHeat`. Le vent n'est pas un solveur de mécanique des fluides ; sa vitesse avec l'altitude est paramétrée. Les précipitations arrivent instantanément au sol ; pas de transport vertical progressif des gouttes ni de réévaporation pendant leur chute. Les nuages restent rendus sur un overlay 2D projeté et non sur six volumes WebGL.

Conservés : 2 × 2 km ; 10 m/cellule ; 2 000 pas/jour ; rivières, nappes, neige, végétation ; animaux désactivés. Lire [le journal de validation](PROGRESS.md).
