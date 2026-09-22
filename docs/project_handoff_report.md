# Project Handoff — Simu_monde

**Phase :** 1 — noyau initial  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur d'écosystème 2D continu où des comportements complexes émergent de règles locales, de l'environnement et plus tard de la mémoire.

## Décisions déjà prises

1. Monde 2D continu.
2. Coordonnées réelles `(x, y)` en mètres.
3. Taille par défaut 1000 m × 1000 m, configurable.
4. Frontières V1 = murs infranchissables.
5. Core exécutable headless.
6. Fixed timestep.
7. RNG seedé et reproductible.
8. Déterminisme = replay reproductible, pas comportement simpliste.
9. L'intelligence recherchée est émergente/adaptative.
10. **Pygame est le viewer V1**, strictement séparé du core.
11. Le core stocke les positions en mètres ; l'adapter convertit en pixels.
12. L'orientation visuelle V1 utilise une origine logique bas-gauche, X vers la droite, Y vers le haut.

## Frontière core / interface

```text
CORE
position = (x_m, y_m)
simulation time
world state
rules
    |
    | lecture / snapshot
    v
PYGAME ADAPTER
camera
meters -> pixels
drawing
input controls
```

Aucune loi du monde ne doit dépendre de Pygame ou du framerate.

## État du code

Le world kernel déterministe a été mergé via PR #5 :

- `SimulationConfig`;
- `Position2D`;
- `WorldBounds`;
- `SimulationClock`;
- `SeededRNG`;
- `World`;
- `Simulation.step()`.

## Prochaine interface minimale

Créer un viewer Pygame capable d'afficher :

- le rectangle du monde ;
- une ou plusieurs positions de test provenant du core ;
- tick / temps ;
- transformation réversible et testable mètres -> pixels.

Pas encore d'eau, plante ou animal nécessaire à cette étape.
