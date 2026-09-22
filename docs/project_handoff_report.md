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
15. Avant chaque délégation Codex, le pilote doit proposer à Jude le **modèle + niveau de raisonnement** adaptés, avec une justification courte et en privilégiant l'efficacité de quota. Cette règle s'applique à tous les futurs pilotes.

## État du code

Mergé :

- world kernel déterministe (#5) ;
- viewer Pygame + executable Windows (#9).

Le viewer permet déjà :

- pause / run ;
- single-step ;
- tick / temps ;
- monde redimensionnable sans modifier l'état du core.

## Étape active — végétation minimale

Issue #10.

La première entité écologique sera une plante avec :

- ID stable ;
- position continue ;
- biomasse comestible en kg ;
- biomasse maximale ;
- vitesse de repousse ;
- placement initial déterministe à partir du RNG du monde.

La croissance est volontairement simplifiée comme un apport externe de biomasse. Aucun cycle de l'eau ou de nutriments n'est encore modélisé.

## Expérience cible

Après les plantes, ajouter un herbivore très simple puis sa mémoire.

On ne programmera pas directement :

- migration ;
- troupeau ;
- territoire ;
- habitudes ;
- chemins préférés.

On programmera seulement les mécanismes locaux nécessaires et on observera si ces phénomènes apparaissent d'eux-mêmes.

## Ordre immédiat

```text
#10 plantes
  ↓
herbivore minimal
  ↓
mémoire minimale
  ↓
observer / mesurer l'émergence
  ↓
#2 eau (deferred)
```
