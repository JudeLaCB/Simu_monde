# Roadmap — Simu_monde

## Philosophie

Chaque phase doit produire un monde observable plus riche sans casser les invariants déjà validés.

La complexité recherchée doit émerger de règles locales, de contraintes, de mémoire et de rétroactions, tout en restant reproductible pour une seed donnée.

## Phase 0 — Fondations

Terminé :

- gouvernance ;
- architecture headless ;
- tests/CI ;
- monde 2D continu ;
- 1000 m × 1000 m configurables ;
- murs V1 ;
- principe d'émergence.

## Phase 1A — Deterministic world kernel

Terminé via PR #5 :

- `SimulationConfig`;
- `Position2D`;
- `WorldBounds`;
- `SimulationClock`;
- `SeededRNG`;
- `World`;
- `Simulation.step()`.

## Phase 1V — Première visualisation 2D

Viewer Pygame minimal :

- fenêtre 2D ;
- monde rendu comme rectangle ;
- conversion mètres -> pixels ;
- origine logique bas-gauche ;
- affichage de positions fournies par le core ;
- tick et temps ;
- séparation stricte core / interface.

Aucune règle d'écologie dans le viewer.

## Phase 1B — Première ressource : eau

Ensuite :

- réservoirs d'eau ;
- transferts explicites ;
- conservation ;
- métriques.

## Phase 1C — Végétation minimale

Ajouter une végétation simple.

## Phase 1D — Animal minimal

Ajouter un animal avec position continue et besoins.

## Phase 1E — Mémoire minimale

Première mémoire individuelle utile :

- souvenir d'une ressource ou d'un danger ;
- ancienneté du souvenir ;
- confiance simple ;
- décision dépendant à la fois de la perception actuelle et de la mémoire.

Objectif : produire les premiers comportements adaptatifs sans script global.

## Phases suivantes

Cycles écologiques, mémoire plus riche, interactions, reproduction, évolution, environnement, puis optimisation selon les limites observées.
