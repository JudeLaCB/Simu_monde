# Roadmap — Simu_monde

## Philosophie

Chaque phase doit produire un monde observable plus riche sans casser les invariants déjà validés.

## Phase 0 — Fondations

Objectif : rendre le projet prêt pour un développement multi-agent propre.

Décision spatiale actuelle : **la V1 est un monde 2D**.

Les détails spatiaux restent à décider un sujet à la fois.

## Phase 1 — Premier monde headless

### 1A — Clock + resource ledger

Créer :

- World ;
- fixed timestep ;
- RNG seedé ;
- ledger d'eau ;
- métriques ;
- test de conservation.

### 1B — Espace 2D minimal

À définir seulement après décision explicite sur :

- grille ou continu ;
- dimensions ;
- frontières ;
- coordonnées.

### 1C — Végétation minimale

Ajouter ensuite une végétation simple dans l'espace 2D approuvé.

### 1D — Animal minimal

Ajouter ensuite un animal simple avec position et besoins.

## Phase 2 — Première visualisation 2D

Choisir le moyen de visualisation uniquement après que l'espace logique 2D soit défini.

Première vue envisagée :

- monde ;
- eau ;
- plantes ;
- animaux ;
- pause / vitesse ;
- métriques.

La visualisation reste un adapter du core.

## Phases suivantes

Environnement, écologie, physique plus riche, reproduction, génétique et optimisation ne seront détaillés qu'une fois les fondations spatiales et écologiques stables.
