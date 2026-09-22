# Roadmap — Simu_monde

## Philosophie

Chaque phase doit produire un monde observable plus riche sans casser les invariants déjà validés.

La complexité recherchée doit émerger autant que possible de règles locales, de contraintes et de rétroactions, tout en restant reproductible avec une seed donnée.

## Phase 0 — Fondations

Objectif : rendre le projet prêt pour un développement multi-agent propre.

Décisions spatiales actuelles :

- V1 en 2D ;
- espace continu ;
- positions réelles `(x, y)` ;
- taille par défaut 1000 m × 1000 m ;
- dimensions configurables à terme ;
- frontières V1 = murs infranchissables.

Les autres détails restent à décider un sujet à la fois.

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

Créer ensuite :

- dimensions configurées du monde ;
- position 2D continue ;
- validation d'appartenance au domaine ;
- frontière de type mur ;
- tests de bornes.

Le comportement précis d'une entité mobile contre un mur sera spécifié avec le système de mouvement.

### 1C — Végétation minimale

Ajouter ensuite une végétation simple dans l'espace 2D continu approuvé.

### 1D — Animal minimal

Ajouter ensuite un animal simple avec position continue et besoins.

Le comportement ne doit pas être réduit à une animation scriptée : les décisions doivent dépendre de l'état et des perceptions du monde.

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

Environnement, mémoire/comportement plus riche, écologie, physique, reproduction, génétique et optimisation seront détaillés progressivement à partir des limites observées.
