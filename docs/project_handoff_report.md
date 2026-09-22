# Project Handoff — Simu_monde

**Phase :** 0 — fondations  
**État :** bootstrap initial en préparation  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur d'écosystème par complexité progressive.

La V1 est volontairement **strictement 2D**.

## Décisions déjà prises

1. Le premier monde est 2D.
2. Le core de simulation doit fonctionner headless.
3. La visualisation est un adapter, pas l'autorité sur l'état écologique.
4. Le temps de simulation utilise un fixed timestep.
5. Le hasard doit être seedé et reproductible.
6. Les unités, sources, puits et invariants sont explicites.
7. On commence avec des modèles simples puis on les raffine.

## Décisions volontairement non prises

- grille ou espace continu ;
- taille du monde ;
- frontières ;
- représentation spatiale de l'eau ;
- moteur de visualisation 2D.

Chaque sujet sera traité séparément.

## Stack Phase 0

- Python >= 3.11 ;
- pytest ;
- Hypothesis ;
- Ruff ;
- mypy ;
- GitHub Actions.

## Prochaine étape recommandée

Avant d'implémenter l'espace, décider **un seul sujet spatial à la fois**.

Le prochain sujet naturel est : **grille discrète ou espace 2D continu ?**

La Phase 1A technique (clock + resource ledger) reste préparée, mais l'espace ne doit pas être inventé par Codex avant validation.
