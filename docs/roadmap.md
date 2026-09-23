# Roadmap — Simu_monde

## Philosophie

Chaque phase doit produire un monde observable plus riche sans casser les invariants déjà validés.

La complexité recherchée doit émerger de règles locales, de contraintes, de mémoire et de rétroactions, tout en restant reproductible pour une seed donnée.

## Phases terminées

### Phase 0 — Fondations

Terminé :

- gouvernance ;
- architecture headless ;
- tests/CI ;
- monde 2D continu ;
- 1000 m × 1000 m configurables ;
- murs V1 ;
- principe d'émergence.

### Phase 1A — Deterministic world kernel

Terminé via PR #5.

### Phase 1V — Première visualisation 2D

Terminé via PR #9 :

- viewer Pygame ;
- pause / run / single-step ;
- affichage tick / temps ;
- build Windows `SimuMonde.exe`.

### Phase 1C — Végétation minimale

Terminé via PR #12.

### Phase 1D — Herbivore minimal

Terminé via PR #15 :

- faim ;
- perception locale ;
- recherche de plante ;
- alimentation ;
- exploration seedée ;
- réflexion aux murs ;
- plusieurs herbivores sans règle sociale.

## Priorité actuelle — fermer le cycle de l'eau

Nouvel ordre décidé :

```text
végétation
    ↓
herbivores
    ↓
cycle fermé de l'eau + soif
    ↓
observer les limites écologiques
    ↓
mémoire
    ↓
complexité supplémentaire
```

Le but est désormais de voir comment un deuxième besoin concurrent et une ressource strictement conservée modifient spontanément les comportements existants.

## Phase 1F — Closed Water Cycle V1

Étape active — Issue #2.

Ajouter :

- eau atmosphérique globale ;
- eau du sol globale ;
- points d'eau spatiaux ;
- eau corporelle des herbivores ;
- pluie déterministe ;
- évaporation ;
- croissance des plantes limitée par l'eau ;
- transpiration simplifiée ;
- soif et boisson ;
- invariant strict de conservation de l'eau.

Invariant central :

```text
atmosphère
+ sol
+ surface
+ eau corporelle
= constante
```

La pluie n'a pas besoin d'être représentée graphiquement.

La disparition d'eau accessible peut bloquer croissance et abreuvement même si la quantité totale d'eau du monde reste constante.

## Phase suivante — Mémoire minimale

Après observation du système eau + faim :

- souvenir d'une ressource ;
- ancienneté ;
- confiance ;
- oubli ;
- décision influencée par perception actuelle + mémoire.

La mémoire ne doit pas être ajoutée avant d'avoir observé les limites du système actuel à deux besoins.

## Phases ultérieures

Cycles de vie, reproduction, mort, ressources supplémentaires, environnement plus riche, évolution puis optimisation selon les limites réellement observées.
