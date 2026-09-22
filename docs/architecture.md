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
      Headless Adapter                  Pygame Adapter
   batch / tests / metrics          camera / drawing / input
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

Le core ne doit pas importer Pygame ni aucun autre moteur de rendu.

### Systems

Chaque système transforme une partie explicite du monde.

### Models

Les modèles portent les équations/approximations remplaçables : évaporation, croissance, métabolisme, vision, coût de locomotion, etc.

### Adapters

Les adapters connectent le core à l'extérieur :

- runner headless ;
- visualisation 2D ;
- sauvegarde/chargement ;
- export métriques ;
- interface utilisateur.

La visualisation lit l'état du core et le transforme en pixels. Elle n'est jamais la source de vérité des coordonnées ou des règles.

## 4. Espace V1

Décisions actuelles :

- monde **2D** ;
- espace **continu** ;
- chaque entité spatiale utilise des coordonnées réelles `(x, y)` ;
- dimensions initiales : **1000 m × 1000 m** ;
- dimensions configurables ;
- limites = **murs infranchissables**.

Domaine spatial initial :

```text
0 <= x <= world_width_m
0 <= y <= world_height_m
```

## 5. Visualisation V1

Décision : utiliser **Pygame** pour la première interface réelle.

Pygame appartient uniquement à `src/simu_monde/adapters/`.

Le core conserve les coordonnées en mètres. Le viewer applique une transformation explicite vers les pixels :

```text
screen_x = world_x / world_width * viewport_width
screen_y = viewport_height - (world_y / world_height * viewport_height)
```

Convention de visualisation V1 :

- origine logique du monde : bas-gauche ;
- axe X vers la droite ;
- axe Y vers le haut ;
- inversion de Y uniquement dans l'adapter Pygame, car l'écran utilise une origine en haut-gauche.

La première interface doit seulement pouvoir afficher :

- les limites du monde ;
- des positions 2D fournies par le core ;
- le tick et le temps de simulation ;
- éventuellement pause/step si cela reste dans l'adapter.

La visualisation ne doit pas :

- modifier directement les coordonnées internes ;
- contenir des règles d'écologie ;
- contenir les décisions des animaux ;
- déterminer le temps de simulation à partir du framerate ;
- devenir nécessaire pour exécuter les tests du core.

## 6. Temps

La simulation utilise un **fixed timestep**. Le framerate Pygame est indépendant du temps du monde.

## 7. Déterminisme

Même version + même configuration + même état initial + même seed + mêmes entrées => même trajectoire observable.

La présence ou l'absence du viewer Pygame ne doit pas modifier cette trajectoire.

## 8. Données et unités

- temps : seconde ;
- distance : mètre ;
- masse : kilogramme ;
- énergie : joule lorsque nécessaire ;
- eau : kilogramme d'eau par défaut.

## 9. Performance

Priorité : exactitude, déterminisme, observabilité, simplicité, puis performance mesurée.
