# Project Handoff — Simu_monde

**Phase :** 0 — fondations  
**État :** bootstrap initial en préparation  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur d'écosystème par complexité progressive.

La V1 est volontairement **strictement 2D, continue et bornée**.

## Décisions déjà prises

1. Le premier monde est 2D.
2. L'espace est continu, pas une grille de cases.
3. Les entités spatiales utilisent des coordonnées réelles `(x, y)`.
4. Le monde V1 mesure par défaut **1000 m × 1000 m**.
5. Les dimensions appartiennent à la configuration du monde afin de pouvoir évoluer plus tard.
6. Les limites du monde se comportent comme des murs infranchissables en V1.
7. La politique de frontière pourra être remplacée plus tard par des comportements plus riches ou punitifs, sans que ces variantes appartiennent à la V1.
8. Le core de simulation doit fonctionner headless.
9. La visualisation est un adapter, pas l'autorité sur l'état écologique.
10. Le temps de simulation utilise un fixed timestep.
11. Le hasard doit être seedé et reproductible.
12. Les unités, sources, puits et invariants sont explicites.
13. On commence avec des modèles simples puis on les raffine.
14. Le projet vise une **intelligence émergente/adaptative** : le déterminisme garantit la reproductibilité, pas des comportements simplistes.

## Principe d'intelligence du monde

Une entité doit pouvoir réagir au contexte à partir de règles locales, de son état, de ses perceptions et plus tard de sa mémoire.

Exemple :

```text
même seed + même état initial
=> même histoire

mais

état local différent
=> décision différente
```

Les comportements complexes doivent autant que possible émerger de boucles de rétroaction plutôt que de scripts globaux.

## Décisions volontairement non prises

- réaction dynamique exacte lorsqu'une entité touche un mur ;
- origine/orientation visuelle des axes ;
- représentation spatiale de l'eau ;
- éventuelle grille secondaire pour le sol/climat ;
- moteur de visualisation 2D ;
- architecture précise de décision/mémoire des animaux.

Chaque sujet sera traité séparément.

## Stack Phase 0

- Python >= 3.11 ;
- pytest ;
- Hypothesis ;
- Ruff ;
- mypy ;
- GitHub Actions.

## Prochaine décision conceptuelle

Le cadre spatial de base est désormais suffisamment défini pour préparer l'espace continu.

Le prochain sujet comportemental important sera de définir comment obtenir des comportements adaptatifs sans perdre le déterminisme.
