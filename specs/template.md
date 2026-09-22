# Feature / Model Spec

## Status

DRAFT | APPROVED | IMPLEMENTED

## Goal

Quel phénomène ou comportement doit devenir observable ?

## Scope

Ce qui entre dans cette feature.

## Non-goals

Ce qui reste explicitement hors scope.

## State variables

| Variable | Meaning | Unit | Bounds |
|---|---|---|---|
| | | | |

## Inputs / outputs

### Inputs

- ...

### Outputs

- ...

## Model / rules

Décrire les équations, transitions ou règles suffisamment précisément pour qu'elles puissent être implémentées sans invention.

## Sources / sinks / transfers

Pour chaque ressource concernée :

```text
source -> stock -> stock -> sink
```

## Execution order

Position de ce système dans le tick.

## Randomness

- RNG utilisé ?
- seed ?
- distribution ?
- ordre des tirages observable ?

## Invariants

- ...

## Edge cases

- zéro ;
- valeurs extrêmes ;
- ressource insuffisante ;
- mort/suppression ;
- grands `dt` ;
- frontières spatiales ;
- NaN/Inf.

## Acceptance criteria

- [ ] ...
- [ ] ...

## Tests

- unit :
- property/invariant :
- integration :
- deterministic scenario :
- timestep sensitivity :
- performance si nécessaire :

## Architecture touch points

Fichiers/modules/interfaces concernés.

## Forbidden changes

Ce que Codex ne doit pas modifier ou généraliser.

## STOP conditions

Décisions qui doivent revenir au Primary/Jude au lieu d'être inventées pendant l'implémentation.
