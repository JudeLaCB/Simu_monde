# Project Handoff — Simu_monde

**Phase :** 1 — première expérience d'émergence  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur 2D continu où des comportements surprenants émergent de règles locales simples, de contraintes environnementales et de mémoire, tout en restant parfaitement rejouables avec la même seed.

## Décisions déjà prises

1. Monde 2D continu.
2. Coordonnées réelles `(x, y)` en mètres.
3. Taille par défaut 1000 m × 1000 m, configurable.
4. Frontières V1 = murs infranchissables.
5. Core exécutable headless.
6. Fixed timestep.
7. RNG seedé et reproductible.
8. Déterminisme = replay reproductible, pas comportement simpliste.
9. L'intelligence recherchée est émergente/adaptative.
10. Pygame est le viewer V1, strictement séparé du core.
11. Le core stocke les positions en mètres ; l'adapter convertit en pixels.
12. L'orientation visuelle V1 utilise une origine logique bas-gauche, X vers la droite, Y vers le haut.
13. `SimuMonde.exe` est produit par le workflow Windows.
14. La première expérience d'émergence suit l'ordre : **plantes -> herbivore -> mémoire -> eau**.
15. Avant chaque délégation Codex, le pilote doit proposer à Jude le **modèle + niveau de raisonnement** adaptés, avec une justification courte et en privilégiant l'efficacité de quota.

## État du code

Mergé :

- world kernel déterministe (#5) ;
- viewer Pygame + executable Windows (#9) ;
- végétation minimale (#12).

La végétation actuelle possède :

- position continue ;
- biomasse comestible ;
- biomasse maximale ;
- repousse déterministe ;
- placement seedé ;
- rendu depuis le core.

## Étape active — herbivore minimal

Issue #13.

Le premier animal doit posséder uniquement les mécanismes nécessaires à la boucle locale :

```text
faim
  ↓
perception locale
  ↓
plante visible la plus proche
  ↓
déplacement ou alimentation
  ↓
biomasse végétale modifiée
  ↓
décision suivante modifiée
```

Sans plante visible ou lorsqu'il n'a pas suffisamment faim, il explore via une direction persistante légèrement perturbée par le RNG seedé.

Le contact avec les murs utilise maintenant une réflexion simple de la direction.

## Règles volontairement absentes

Ne pas programmer directement :

- mémoire ;
- troupeau ;
- migration ;
- territoire ;
- attraction sociale ;
- chemins préférés ;
- reproduction ;
- mort ;
- eau.

Ces comportements ne doivent apparaître que plus tard, soit par nouveaux mécanismes locaux explicites, soit comme phénomènes émergents.

## Ordre immédiat

```text
#13 herbivore minimal
  ↓
mémoire minimale
  ↓
observer / mesurer l'émergence
  ↓
#2 eau (deferred)
```

## Modèle Codex

Avant chaque délégation Codex, le pilote annonce le modèle et le niveau de reasoning recommandés selon la tâche actuelle. Pour l'implémentation de #13, recommandation actuelle : **GPT-5.6 Sol — Medium reasoning**.
