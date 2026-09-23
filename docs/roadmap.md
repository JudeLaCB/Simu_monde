# Roadmap — Simu_monde

## Philosophie

Chaque phase doit enrichir le monde sans programmer directement les phénomènes que l'on souhaite observer.

Le projet cherche désormais à faire émerger les comportements à partir de :

- contraintes physiques ;
- ressources ;
- homéostasie ;
- mortalité ;
- cycles de matière ;
- interactions entre espèces ;
- puis mémoire et apprentissage.

Le replay reste déterministe pour une seed donnée.

## Phases terminées

### Phase 0 — Fondations

Terminé.

### Phase 1A — Deterministic world kernel

Terminé via PR #5.

### Phase 1V — Viewer Pygame

Terminé via PR #9.

### Phase 1C — Végétation minimale

Terminé via PR #12.

### Phase 1D — Herbivore minimal

Terminé via PR #15.

### Phase 1F — Closed Water Cycle V1

Terminé via PR #17 :

- atmosphère ;
- eau du sol ;
- points d'eau spatiaux ;
- eau corporelle ;
- pluie ;
- évaporation ;
- croissance végétale limitée par l'eau ;
- soif ;
- conservation stricte de l'eau.

## Observation actuelle

Les règles à seuil créent des attracteurs forts :

- d'abord autour des plantes ;
- puis autour des points d'eau.

Plutôt que d'ajouter des exceptions comportementales, la prochaine étape remplace ces seuils par une régulation interne inspirée d'un PID.

## Phase 1G — Homéostasie, vieillissement, mort et cadavres

**Étape active — Issue #18**

Ajouter :

- réserve énergétique explicite en joules ;
- coût métabolique basal ;
- coût énergétique du mouvement ;
- énergie récupérée par alimentation ;
- régulateur homéostatique PID-inspired pour nourriture et eau ;
- vieillissement des plantes et herbivores ;
- mort des herbivores par famine ou vieillesse ;
- mort des plantes par vieillesse ;
- cadavres spatiaux persistants ;
- conservation de l'eau incluant l'eau des cadavres.

La consigne conceptuelle est :

```text
survie / maintien des réserves
```

Le contrôleur ne programme pas directement "manger" ou "boire" ; il produit des urgences internes concurrentes.

## Phase 1H — Décomposition et cycle local des nutriments

**Préparée — Issue #19**

Après validation de 1G :

```text
cadavre
   ↓
décomposition
   ↓
nutriments locaux + retour d'eau au sol
   ↓
croissance végétale
```

Un champ spatial déterministe de nutriments permettra à la mort de modifier la géographie future du monde.

## Phase 1I — Reproduction minimale

Ajouter seulement après que mortalité et matière recyclée soient stables.

Objectif :

- renouveler les populations ;
- éviter une extinction mathématiquement garantie ;
- permettre l'observation de dynamiques de population durables.

## Phase 1J — Prédateur minimal

Introduire ensuite un prédateur soumis au même principe de survie :

- énergie ;
- eau ;
- âge ;
- perception locale ;
- urgence alimentaire ;
- poursuite ;
- capture.

L'herbivore recevra alors un signal de danger concurrent de faim/soif.

Aucune règle de troupeau, migration ou territoire ne sera codée explicitement.

## Mémoire

La mémoire reste prévue, mais volontairement après l'observation des dynamiques de survie, mortalité, recyclage, reproduction et prédation.

## Direction générale

```text
eau + végétation + herbivores
        ↓
homéostasie
        ↓
mort
        ↓
cadavres
        ↓
nutriments locaux
        ↓
reproduction
        ↓
prédateur
        ↓
mémoire / apprentissage
```
