# Project Handoff — Simu_monde

**Phase active :** 1G — Homeostasis, Ageing, Death and Carcasses  
**Source de vérité live :** GitHub

## Vision

Construire un simulateur 2D continu où les comportements émergent de besoins internes, de contraintes physiques et de cycles de matière, plutôt que de règles comportementales globales.

## État mergé

Principales étapes :

- #5 world kernel ;
- #9 viewer Pygame ;
- #12 végétation ;
- #15 herbivores ;
- #17 cycle fermé de l'eau.

Le monde possède maintenant :

- plantes spatiales ;
- herbivores mobiles ;
- perception locale ;
- alimentation ;
- exploration seedée ;
- eau atmosphérique ;
- eau du sol ;
- points d'eau ;
- pluie/évaporation ;
- eau corporelle ;
- invariant strict de conservation de l'eau.

## Observation ayant motivé la nouvelle phase

Les herbivores développent naturellement des attracteurs spatiaux :

1. camping près des plantes ;
2. après introduction de la soif, camping près des points d'eau.

Ce comportement n'est pas corrigé par une règle "quitte la ressource".

À la place, les besoins sont transformés en boucle de régulation interne.

## Phase 1G — Issue #18

L'herbivore remplace le scalar abstrait de faim par une réserve énergétique.

Concept :

```text
réserve cible
   ↓
erreur actuelle
   ↓
P : déficit actuel
I : déficit accumulé
D : vitesse de dégradation
   ↓
urgence nourriture / eau
   ↓
action locale réalisable
```

Le PID-inspired controller arbitre entre les besoins, mais seules les ressources réellement perçues peuvent être ciblées.

## Mortalité

Herbivore :

- famine si énergie = 0 ;
- vieillesse si âge >= durée de vie ;
- pas encore de mort par déshydratation.

Plante :

- durée de vie ;
- mort par vieillesse.

La mort d'un herbivore crée un cadavre spatial persistant.

Le cadavre conserve :

- l'eau corporelle ;
- un stock de nutriment récupérable préparant le cycle suivant.

## Eau

La mort ne détruit pas l'eau :

```text
animal.body_water
→ carcass.water
```

`World.total_water_kg` doit donc inclure l'eau des cadavres.

La tolérance de conservation reste `1e-8 kg`.

## Étape suivante — Issue #19

Après merge de 1G :

- champ local de nutriments ;
- décomposition progressive ;
- eau des cadavres -> sol ;
- nutriments des cadavres -> cellule locale ;
- nutriments des plantes/herbivores suivis explicitement ;
- croissance végétale limitée par eau + nutriments.

## Puis

```text
#18 homéostasie / mortalité
   ↓
#19 décomposition / nutriments
   ↓
reproduction minimale
   ↓
prédateur
   ↓
mémoire
```

## Modèle Codex recommandé pour #18

**GPT-5.6 Sol — High reasoning**

Raison : migration du modèle comportemental, nouvel état persistant PID, coûts énergétiques, mutations de collections, mortalité et conservation de l'eau doivent rester cohérents ensemble.

## Règles toujours actives

- pas d'ECS prématuré ;
- pas de scheduler générique ;
- pas de mémoire dans 1G ;
- pas de reproduction ;
- pas de prédateur ;
- pas de décomposition avant #19 ;
- Pygame reste présentation-only ;
- tout nouveau comportement doit rester local et rejouable.
