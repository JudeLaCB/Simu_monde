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

## 3. Frontières architecturales

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
- chaque entité spatiale utilise des coordonnées réelles `(x, y)` ;
- dimensions initiales : **1000 m × 1000 m** ;
- les dimensions doivent rester un paramètre de monde, même si la V1 utilise cette valeur par défaut ;
- les limites agissent comme des **murs infranchissables**.

Domaine spatial initial :

```text
0 <= x <= world_width_m
0 <= y <= world_height_m

world_width_m  = 1000
world_height_m = 1000
```

Une entité ne peut pas sortir du domaine. Le comportement exact de collision/réaction au mur sera défini avant implémentation du mouvement.

La politique de frontière doit rester remplaçable à terme. Des variantes futures pourront introduire par exemple une zone dangereuse, un coût énergétique, des dégâts ou une autre conséquence écologique. Ces comportements ne font pas partie de la V1.

Non décidé à ce stade :

- type numérique exact des coordonnées ;
- orientation visuelle des axes ;
- comportement dynamique exact lors d'un contact avec un mur ;
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

Le déterminisme est une propriété de reproductibilité, pas une obligation de comportement simple. Des décisions complexes et adaptatives peuvent rester déterministes si elles dépendent uniquement de l'état du monde, de la mémoire de l'entité et d'un RNG seedé.

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
