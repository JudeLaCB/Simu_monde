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

Une formule plus réaliste n'est ajoutée que lorsqu'elle répond à une limite observée.

## 3. Unités obligatoires

Chaque variable importante documente son unité.

Préférer :

```text
water_kg = 50.0
energy_j = 80.0
hunger_level = 0.7  # dimensionless [0, 1]
```

## 4. Fixed timestep

Les règles du monde sont mises à jour avec un pas de temps fixe.

Le rendu n'appelle pas directement les lois biologiques selon son framerate.

Tout changement de `dt` doit être testé sur les observables principaux.

## 5. Déterminisme reproductible

Toute stochasticité doit pouvoir être reproduite par seed.

Les scénarios de régression stockent au minimum :

- version/config ;
- seed ;
- durée ;
- métriques attendues ou bornes attendues.

Le déterminisme signifie :

```text
même version
+ même configuration
+ même état initial
+ même seed
+ mêmes entrées
= même trajectoire observable
```

Il ne signifie pas que les entités doivent suivre des comportements rigides ou triviaux.

## 6. Intelligence émergente et adaptation

Le projet vise une nature qui puisse paraître **adaptative et intelligente** sans sacrifier la reproductibilité.

La complexité doit venir principalement de :

- perception locale ;
- besoins internes ;
- choix dépendant du contexte ;
- mémoire lorsque nécessaire ;
- coûts et bénéfices concurrents ;
- rétroactions environnementales ;
- interactions entre entités ;
- apprentissage ou évolution uniquement lorsqu'ils deviennent utiles.

Exemple d'un animal déterministe mais adaptatif :

```text
soif élevée
+ eau A proche mais zone risquée
+ eau B plus loin mais connue comme sûre
+ énergie disponible
+ mémoire récente
→ choix calculé à partir du contexte
```

Avec la même seed et le même historique, le choix est reproductible. Si l'état du monde change, la décision peut changer.

Les comportements complexes doivent autant que possible **émerger de règles locales** plutôt que d'être imposés par un script global.

## 7. Bilans et invariants

Exemple futur pour l'eau :

```text
W_total =
    W_surface
  + W_soil
  + W_plants
  + W_animals
  + W_atmosphere
  + W_waste
```

Pour la biomasse, ne pas prétendre à une conservation physique si le modèle simplifié ne la représente pas.

## 8. Ordre des systèmes

L'ordre d'exécution influence le résultat. Il doit donc être explicite.

L'ordre exact sera défini par les specs des systèmes concernés.

## 9. Validation scientifique proportionnelle

Trois niveaux possibles :

1. **cohérence interne** — invariants et absence d'états impossibles ;
2. **plausibilité** — ordre de grandeur et comportement qualitatif ;
3. **validation externe** — comparaison à données ou littérature.

Ne pas présenter un modèle plausible comme scientifiquement validé.

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

Un bug de simulation doit pouvoir être diagnostiqué sans regarder uniquement la visualisation.
