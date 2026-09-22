# Project Handoff — Simu_monde

**Phase :** 0 — fondations  
**État :** bootstrap initial en préparation  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur d'écosystème par complexité progressive.

La V1 est volontairement **strictement 2D et continue**.

## Décisions déjà prises

1. Le premier monde est 2D.
2. L'espace est continu, pas une grille de cases.
3. Les entités spatiales utilisent des coordonnées réelles `(x, y)`.
4. Le core de simulation doit fonctionner headless.
5. La visualisation est un adapter, pas l'autorité sur l'état écologique.
6. Le temps de simulation utilise un fixed timestep.
7. Le hasard doit être seedé et reproductible.
8. Les unités, sources, puits et invariants sont explicites.
9. On commence avec des modèles simples puis on les raffine.

## Décisions volontairement non prises

- taille du monde ;
- frontières ;
- origine et orientation des axes ;
- représentation spatiale de l'eau ;
- éventuelle grille secondaire pour le sol/climat ;
- moteur de visualisation 2D.

Chaque sujet sera traité séparément.

## Stack Phase 0

- Python >= 3.11 ;
- pytest ;
- Hypothesis ;
- Ruff ;
- mypy ;
- GitHub Actions.

## Prochaine décision spatiale

Définir **la taille et les limites du monde**, sans encore choisir la représentation de l'eau ou du sol.

La Phase 1A technique (clock + resource ledger) reste préparée, mais Codex ne doit pas inventer les conventions spatiales restantes.
