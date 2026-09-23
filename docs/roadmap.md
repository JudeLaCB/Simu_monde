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

Terminé via PR #9 :

- viewer Pygame ;
- transformation mètres -> pixels ;
- fenêtre redimensionnable ;
- pause / run / single-step ;
- affichage tick / temps ;
- build Windows `SimuMonde.exe`;
- séparation stricte core / interface.

## Première expérience d'émergence

Priorité actuelle :

```text
végétation
    ↓
herbivore
    ↓
mémoire
    ↓
premiers comportements émergents
    ↓
eau / deuxième besoin concurrent
```

Le but n'est pas de reproduire tout de suite un écosystème réaliste. Le but est d'obtenir le plus tôt possible un comportement collectif ou individuel intéressant qui n'a pas été scripté explicitement.

## Phase 1C — Végétation minimale

Créer une ressource spatiale vivante simple :

- plante avec ID stable ;
- position continue ;
- biomasse comestible ;
- biomasse maximale ;
- repousse déterministe ;
- placement initial seedé ;
- rendu Pygame depuis l'état du core.

Aucun besoin en eau, reproduction ou mort à ce stade.

## Phase 1D — Herbivore minimal

Ensuite :

- position ;
- faim ;
- vitesse ;
- rayon de perception ;
- déplacement ;
- alimentation ;
- exploration lorsqu'aucune nourriture n'est perçue.

Pas de règle de troupeau, migration ou territoire.

## Phase 1E — Mémoire minimale

Ajouter ensuite la première mémoire individuelle :

- souvenir d'une ressource ;
- ancienneté ;
- confiance simple ;
- oubli ;
- décision influencée par perception actuelle + mémoire.

Objectif : observer si des habitudes, trajets, préférences ou abandons de zones émergent sans règle globale correspondante.

## Phase 1F — Eau / deuxième besoin

L'eau est volontairement différée jusque-là.

Son introduction ajoutera un second besoin spatial concurrent (faim vs soif), ce qui enrichira les décisions sans être nécessaire au premier test d'émergence.

## Phases suivantes

Interactions plus riches, ressources multiples, reproduction, évolution, environnement, puis optimisation selon les limites observées.
