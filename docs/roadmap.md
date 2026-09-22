# Roadmap — Simu_monde

## Philosophie

Chaque phase doit produire un monde observable plus riche sans casser les invariants déjà validés.

## Phase 0 — Fondations

Objectif : rendre le projet prêt pour un développement multi-agent propre.

Décisions spatiales actuelles :

- V1 en 2D ;
- espace continu ;
- positions réelles `(x, y)`.

Les autres détails spatiaux restent à décider un sujet à la fois.

## Phase 1 — Premier monde headless

### 1A — Clock + resource ledger

Créer :

- World ;
- fixed timestep ;
- RNG seedé ;
- ledger d'eau ;
- métriques ;
- test de conservation.

### 1B — Espace 2D continu minimal

Définir ensuite :

- dimensions ;
- frontières ;
- convention des coordonnées ;
- représentation minimale d'une position `(x, y)`.

Aucune grille de cases ne doit être imposée comme espace principal du monde.

### 1C — Végétation minimale

Ajouter ensuite une végétation simple dans l'espace 2D continu approuvé.

### 1D — Animal minimal

Ajouter ensuite un animal simple avec position continue et besoins.

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
