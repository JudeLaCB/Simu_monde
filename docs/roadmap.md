# Roadmap — Simu_monde

## Philosophie

Chaque phase doit produire un monde observable plus riche sans casser les invariants déjà validés.

```text
cycle minimal
→ visualisation
→ nouvelles boucles
→ physique
→ complexité
→ échelle
```

## Phase 0 — Fondations

Objectif : rendre le projet prêt pour un développement multi-agent propre.

Livrables :

- gouvernance légère ;
- architecture core / adapters ;
- principes de simulation ;
- Python package minimal ;
- tests ;
- CI ;
- template de spec.

Critère de sortie : un clone neuf peut installer les dépendances et faire passer les checks.

## Phase 1 — Premier monde headless

### 1A — Clock + resource ledger

Créer :

- World ;
- fixed timestep ;
- RNG seedé ;
- ledger d'eau ;
- métriques ;
- test de conservation.

### 1B — Végétation minimale

Ajouter :

- plante ;
- absorption d'eau ;
- croissance simplifiée ;
- transpiration/évapotranspiration ;
- mort simple si condition extrême.

### 1C — Animal minimal

Ajouter :

- position ;
- soif ;
- faim ;
- énergie ;
- boire ;
- manger ;
- rejets ;
- mort.

Comportement initial :

```text
si soif prioritaire -> chercher/boire
sinon si faim prioritaire -> chercher/manger
sinon -> déplacement simple
```

### 1D — Boucle fermée observable

Objectif :

```text
eau → sol → plante → animal → rejets/décomposition
  ↘ évaporation → atmosphère → retour d'eau
```

Le monde doit tourner headless sur une durée longue avec métriques et invariants.

## Phase 2 — Première visualisation 3D

Choisir le moteur 3D à partir des besoins réellement observés.

Première scène :

- terrain simple ;
- zone d'eau ;
- plantes = primitives ;
- animaux = primitives ;
- caméra ;
- pause / vitesse de simulation ;
- panneau de métriques.

La 3D reste un adapter du core.

## Phase 3 — Environnement

Ajouter progressivement :

- cycle jour/nuit ;
- température ;
- pluie ;
- humidité du sol ;
- saisons simples ;
- topographie si utile.

## Phase 4 — Écologie

Ajouter selon intérêt :

- espèces de plantes ;
- compétition ;
- reproduction ;
- graines ;
- décomposition ;
- nutriments ;
- herbivores multiples ;
- prédateurs.

## Phase 5 — Physique et espace

Seulement lorsque nécessaire :

- locomotion plus physique ;
- pente ;
- collisions ;
- coût énergétique du mouvement ;
- spatial indexing ;
- terrain plus riche.

## Phase 6 — Génétique et évolution

Ajouter :

- traits héritables ;
- mutation ;
- reproduction ;
- coût/bénéfice des traits ;
- sélection naturelle observable.

Critère important : l'évolution doit émerger des règles et contraintes, pas d'un score "fitness" arbitraire ajouté uniquement pour forcer un résultat.

## Phase 7 — Échelle et performance

Après profilage :

- ECS si justifié ;
- partition spatiale ;
- parallélisme ;
- simulations batch ;
- accélération éventuelle.

Aucune optimisation majeure n'est prévue avant mesure.
