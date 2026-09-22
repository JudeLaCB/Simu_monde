# Principes de simulation

## 1. Le monde est un système de stocks et de flux

Une ressource doit être représentée comme un stock identifié et des transformations explicites.

Exemple :

```text
surface_water
  ├─ infiltration -> soil_water
  ├─ drinking -> animal_water
  └─ evaporation -> atmosphere_water
```

Pour une ressource conservée dans un monde fermé :

```text
total(t + dt) = total(t) + external_sources - external_sinks
```

La tolérance numérique doit être explicitée dans les tests.

## 2. Simplicité avant réalisme

Un modèle V1 peut être volontairement faux dans le détail s'il est :

- explicite ;
- cohérent ;
- testable ;
- remplaçable ;
- suffisant pour observer le phénomène recherché.

Exemple d'évaporation initiale :

```text
evaporation = k * exposed_water * dt
```

Une formule plus réaliste n'est ajoutée que lorsqu'elle répond à une limite observée.

## 3. Unités obligatoires

Chaque variable importante documente son unité.

Éviter :

```text
water = 50
energy = 80
```

Préférer un contrat clair :

```text
water_kg = 50.0
energy_j = 80.0
```

ou, si l'unité est abstraite :

```text
hunger_level = 0.7  # dimensionless [0, 1]
```

## 4. Fixed timestep

Les règles du monde sont mises à jour avec un pas de temps fixe.

Le rendu n'appelle pas directement les lois biologiques selon son framerate.

Tout changement de `dt` doit être testé sur les observables principaux.

## 5. Déterminisme

Toute stochasticité doit pouvoir être reproduite par seed.

Les scénarios de régression stockent au minimum :

- version/config ;
- seed ;
- durée ;
- métriques attendues ou bornes attendues.

## 6. Bilans et invariants

Exemples futurs :

### Eau

```text
W_total =
    W_surface
  + W_soil
  + W_plants
  + W_animals
  + W_atmosphere
  + W_waste
```

### Biomasse

Selon le niveau de modélisation, la biomasse pourra être suivie comme stock simplifié avec des sources externes déclarées, par exemple photosynthèse, et des pertes explicites.

Ne pas prétendre à une conservation physique si le modèle simplifié ne la représente pas.

## 7. Ordre des systèmes

L'ordre d'exécution influence le résultat. Il doit donc être explicite.

Exemple futur :

```text
climate
→ water transfer
→ plant growth
→ animal decisions
→ movement
→ feeding/drinking
→ metabolism
→ waste/death
→ decomposition
→ metrics
```

Cet ordre n'est pas encore autorité pour l'implémentation ; il sert d'exemple. La spec du vertical slice fixera l'ordre exact.

## 8. Émergence

Les comportements complexes doivent autant que possible émerger de règles locales simples plutôt que d'être scriptés globalement.

Exemple :

- soif augmente ;
- l'animal cherche de l'eau ;
- l'eau est spatialement limitée ;
- déplacement coûte de l'énergie.

Une migration peut alors émerger sans écrire une règle "migrer".

## 9. Validation scientifique proportionnelle

Trois niveaux possibles :

1. **cohérence interne** — invariants et absence d'états impossibles ;
2. **plausibilité** — ordre de grandeur et comportement qualitatif ;
3. **validation externe** — comparaison à données ou littérature.

La plupart des premières features viseront 1 puis 2. Ne pas présenter un modèle plausible comme scientifiquement validé.

## 10. Observabilité

Chaque système significatif doit fournir des métriques utiles.

Exemples :

- eau totale ;
- eau par réservoir ;
- biomasse végétale ;
- nombre d'animaux ;
- énergie moyenne ;
- morts par cause ;
- temps CPU par tick.

Un bug de simulation doit pouvoir être diagnostiqué sans regarder uniquement l'animation 3D.
