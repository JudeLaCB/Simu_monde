# Architecture — Simu_monde

## 1. Objectif

Construire un monde 3D progressivement plus riche sans rendre les règles de simulation dépendantes du rendu, du moteur physique ou du nombre d'images par seconde.

Le système doit pouvoir :

- exécuter rapidement une simulation sans affichage ;
- reproduire un scénario avec une seed fixe ;
- observer les bilans de ressources ;
- remplacer un modèle simple par un modèle plus réaliste ;
- brancher une visualisation 3D sans déplacer la logique métier ;
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
      Headless Adapter                      3D Adapter
   batch / tests / metrics            scene / camera / input
             |                                 |
        CSV / JSON / plots              future 3D engine
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

Le core ne doit pas importer un moteur 3D.

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

Un système ne doit pas modifier arbitrairement l'état d'un autre domaine sans contrat de flux clair.

### Models

Les modèles portent les équations/approximations remplaçables : évaporation, croissance, métabolisme, vision, coût de locomotion, etc.

Un modèle simple peut être remplacé sans réécrire l'orchestration globale.

### Adapters

Les adapters connectent le core à l'extérieur :

- runner headless ;
- visualisation 3D ;
- sauvegarde/chargement ;
- export métriques ;
- interface utilisateur.

La 3D reçoit idéalement un snapshot immuable ou une vue contrôlée du monde.

## 4. Temps

La simulation utilise un **fixed timestep**.

```text
simulation_time += dt
run systems(dt)
emit metrics/snapshot
```

Le rendu peut être à 30, 60 ou 144 FPS sans changer la trajectoire scientifique du monde.

Les décisions futures sur sous-stepping, intégrateurs avancés ou multi-rate systems seront HIGH-RISK.

## 5. Déterminisme

Le hasard passe par un service RNG seedé appartenant au core.

Les appels aléatoires ne doivent pas être dispersés derrière des APIs globales non contrôlées.

Objectif :

```text
same version + same config + same seed + same inputs
=> same observable simulation trajectory
```

## 6. Données et unités

Convention initiale :

- temps : seconde ;
- distance : mètre ;
- masse : kilogramme ;
- énergie : joule lorsque nécessaire ;
- eau : kilogramme d'eau par défaut, car 1 kg ≈ 1 L aux conditions ordinaires, avec conversion explicite si des litres sont affichés.

Les quantités biologiques qui ne peuvent pas encore être exprimées physiquement peuvent utiliser une unité abstraite nommée, mais jamais une valeur sans unité documentée.

## 7. 3D

Le choix du moteur 3D reste volontairement différé jusqu'au premier vertical slice headless.

Critères de décision :

- simplicité d'intégration avec le core ;
- capacité 3D et physique ;
- exécution headless ;
- tests/automatisation ;
- performances ;
- tooling ;
- coût/licence ;
- facilité de travail avec Codex.

La première visualisation utilisera des primitives simples. Aucun asset complexe n'est requis pour valider l'architecture.

## 8. Performance

Ordre de priorité :

1. exactitude du comportement défini ;
2. déterminisme ;
3. observabilité ;
4. simplicité ;
5. performance mesurée.

Pas d'ECS, multiprocessing, GPU compute ou spatial partitioning avant qu'un profilage montre un besoin.

## 9. Direction long terme

L'architecture doit permettre d'aller vers :

```text
eau + climat
    ↓
sol / nutriments
    ↓
végétation
    ↓
herbivores
    ↓
prédateurs
    ↓
décomposition
    ↓
reproduction / génétique / évolution
```

sans exiger que toutes ces couches existent au départ.
