# Workflow de développement

## 1. Boucle générale

```text
Jude — objectif / choix du comportement
        ↓
Primary Pilot — analyse + modèle + architecture + tests
        ↓
contrat/spec approuvé
        ↓
Codex — code + tests + self-review + PR
        ↓
Primary Pilot — review indépendante
        ↓
Jude — merge
```

## 2. Préparation d'une feature

Pour une feature scientifique ou comportementale, le Primary répond avant code à :

1. quel phénomène veut-on obtenir ?
2. quel est le plus petit modèle suffisant ?
3. quelles variables d'état ?
4. quelles unités ?
5. quelles entrées/sorties ?
6. quelles équations ou règles ?
7. quelles sources/puits ?
8. quel ordre d'exécution ?
9. quels invariants ?
10. quels cas limites ?
11. quels critères d'acceptation ?
12. quels non-goals ?

Le but est que Codex implémente un contrat, pas qu'il invente le modèle en codant.

## 3. Taille des incréments

Préférer les vertical slices minces.

Exemple :

```text
mauvais:
"implémente tout le cycle de la nature"

bon:
"ajoute un ledger d'eau conservatif avec trois réservoirs et un test de bilan"
```

Chaque PR doit idéalement introduire un comportement observable et testable.

## 4. Specs

- SMALL : issue/brief suffisant.
- STANDARD : issue détaillée ou spec légère.
- HIGH-RISK : utiliser `specs/template.md` comme base.

Une spec ne doit pas devenir un essai. Elle doit réduire l'ambiguïté d'implémentation et de review.

## 5. Validation

Pour chaque changement de modèle :

- tests unitaires locaux ;
- au moins un test d'invariant/property si pertinent ;
- scénario déterministe avec seed fixe ;
- validation des bornes ;
- vérification que les métriques permettent le diagnostic.

Pour un changement numérique :

- comparer plusieurs valeurs de `dt` lorsque pertinent ;
- vérifier absence de NaN/Inf ;
- définir les tolérances.

## 6. Review

Le Primary vérifie notamment :

- conformité à la spec ;
- aucune règle du monde inventée ;
- unités explicites ;
- déterminisme préservé ;
- flux/conservation corrects ;
- absence de logique domaine dans le rendu ;
- tests réellement sensibles au bug visé ;
- scope borné.

## 7. Erreur → régression

Toute erreur significative doit si possible devenir :

```text
bug réel
→ scénario minimal reproductible
→ test de régression
→ correction
→ preuve
```

## 8. Complexité et performance

Avant toute optimisation :

1. mesurer ;
2. identifier le bottleneck ;
3. définir un budget ;
4. optimiser derrière la même interface ;
5. prouver que les résultats restent équivalents dans les tolérances.

## 9. Choix de dépendances

Ajouter une dépendance seulement si elle réduit nettement le coût total du projet.

Avant ajout d'un moteur 3D, moteur physique, framework ECS ou librairie scientifique lourde, documenter :

- besoin ;
- alternatives ;
- bénéfice ;
- coût de couplage ;
- testabilité ;
- stratégie de remplacement.
