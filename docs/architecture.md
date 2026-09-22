# Architecture — Simu_monde

## 1. Objectif

Construire d'abord un monde **2D continu** progressivement plus riche, sans rendre les règles de simulation dépendantes du rendu ou du nombre d'images par seconde.

Le système doit pouvoir :

- exécuter rapidement une simulation sans affichage ;
- reproduire un scénario avec une seed fixe ;
- observer les bilans de ressources ;
- remplacer un modèle simple par un modèle plus réaliste ;
- brancher une visualisation 2D sans déplacer la logique métier ;
- monter progressivement en nombre d'entités.

## 2. Architecture logique cible

```text
                       CONFIG / SCENARIO
                              |
                              v
+-------------------------------------------------------------+
|                       SIMULATION CORE                       |
|                                                             |
|  World State <-> Systems Scheduler <-> Simulation Clock     |
|       |                 |                  |                 |
|       |                 +--> RNG seeded    |                 |
|       |                                    |                 |
|       +--> resources / entities / fields / model params     |
|                                                             |
|  Systems: water / plants / animals / decay / climate / ...  |
|                                                             |
|  Invariants + Metrics + Events                              |
+-----------------------------+-------------------------------+
                              |
                         WorldSnapshot
                              |
             +----------------+----------------+
             |                                 |
      Headless Adapter                 Visualisation 2D
   batch / tests / metrics            scene / input / UI
             |                                 |
        CSV / JSON / plots              future 2D adapter
```

## 3. Frontières

### Core

Le core possède :

- le temps du monde ;
- la seed et les générateurs de hasard ;
- l'état des entités et ressources ;
- les règles de transformation ;
- l'ordre des systèmes ;
- les événements simulés ;
- les métriques et bilans.

Le core ne doit pas importer un moteur de rendu.

### Systems

Chaque système transforme une partie explicite du monde.

Exemples futurs :

- WaterCycleSystem
- PlantGrowthSystem
- AnimalNeedsSystem
- FeedingSystem
- WasteSystem
- DecompositionSystem
- ClimateSystem
- ReproductionSystem

### Models

Les modèles portent les équations/approximations remplaçables : évaporation, croissance, métabolisme, vision, coût de locomotion, etc.

### Adapters

Les adapters connectent le core à l'extérieur :

- runner headless ;
- visualisation 2D ;
- sauvegarde/chargement ;
- export métriques ;
- interface utilisateur.

La visualisation reçoit idéalement un snapshot immuable ou une vue contrôlée du monde.

## 4. Espace V1

Décisions actuelles :

- monde **2D** ;
- espace **continu** ;
- chaque entité spatiale utilise des coordonnées réelles `(x, y)`.

Exemple conceptuel :

```text
position = (12.4 m, 37.8 m)
```

La position logique n'est donc pas une case entière d'une grille.

Non décidé à ce stade :

- dimensions du monde ;
- topologie des frontières ;
- type numérique exact des coordonnées ;
- origine et orientation des axes ;
- structures d'indexation spatiale ;
- éventuelle grille secondaire pour des champs environnementaux.

Aucune de ces décisions ne doit être inventée pendant l'implémentation.

## 5. Temps

La simulation utilise un **fixed timestep**.

```text
simulation_time += dt
run systems(dt)
emit metrics/snapshot
```

Le rendu ne doit pas changer la trajectoire scientifique du monde.

## 6. Déterminisme

Le hasard passe par un service RNG seedé appartenant au core.

Objectif :

```text
same version + same config + same seed + same inputs
=> same observable simulation trajectory
```

## 7. Données et unités

Convention initiale :

- temps : seconde ;
- distance : mètre ;
- masse : kilogramme ;
- énergie : joule lorsque nécessaire ;
- eau : kilogramme d'eau par défaut.

## 8. Performance

Ordre de priorité :

1. exactitude du comportement défini ;
2. déterminisme ;
3. observabilité ;
4. simplicité ;
5. performance mesurée.

Pas d'ECS, multiprocessing, GPU compute ou spatial partitioning avant qu'un profilage montre un besoin.
