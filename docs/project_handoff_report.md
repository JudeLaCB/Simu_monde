# Project Handoff — Simu_monde

**Phase :** 1F — Closed Water Cycle V1  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur 2D continu où des comportements complexes émergent de règles locales simples et de ressources contraintes, tout en restant parfaitement rejouables avec une seed donnée.

## État mergé

Le projet possède maintenant :

- noyau déterministe ;
- viewer Pygame + `SimuMonde.exe` ;
- végétation spatiale avec biomasse ;
- herbivores autonomes avec faim ;
- perception locale ;
- alimentation ;
- exploration seedée ;
- réflexion aux murs.

PR principales mergées :

- #5 world kernel ;
- #9 viewer ;
- #12 végétation ;
- #15 herbivore.

## Observation actuelle

Les herbivores peuvent finir par rester près d'une plante renouvelable et exploiter continuellement sa repousse.

Ce comportement n'est pas corrigé artificiellement. Il sert de baseline pour observer comment un second besoin concurrent modifie la dynamique.

## Décision actuelle

Avant d'ajouter la mémoire, introduire un **cycle fermé de l'eau**.

L'eau totale modélisée doit être conservée :

```text
W_total =
    atmosphère
  + sol
  + sources de surface
  + eau corporelle des herbivores
```

L'eau peut devenir inaccessible sans disparaître.

Exemple :

```text
eau totale constante
mais
surface ≈ 0
sol ≈ 0
atmosphère élevée
→ plantes ne poussent plus
→ herbivores ne peuvent plus boire localement
```

## Phase active — Issue #2

La V1 du cycle d'eau comprend :

- pluie déterministe atmosphère -> sol/surface ;
- évaporation sol/surface -> atmosphère ;
- croissance végétale limitée par l'eau du sol ;
- transpiration simplifiée sol -> atmosphère pendant la croissance ;
- eau corporelle de l'herbivore ;
- perte d'eau corporelle -> atmosphère ;
- boisson surface -> corps ;
- soif prioritaire sur la faim au-dessus d'un seuil ;
- points d'eau spatiaux visibles ;
- conservation contrôlée à chaque tick.

## Ordre global approuvé

```text
1. total water before
2. rain
3. plant growth + transpiration
4. herbivore behavior
   - hunger
   - body-water loss
   - thirst priority
   - drinking / feeding / movement
5. evaporation
6. conservation check
7. clock
```

## Règles volontairement absentes

Ne pas ajouter dans cette phase :

- mémoire ;
- mort par déshydratation ;
- reproduction ;
- cycle du carbone ;
- eau stockée dans les plantes ;
- météo réaliste ;
- rivières ;
- nappes phréatiques ;
- humidité locale du sol ;
- pathfinding ;
- ECS.

## Prochaine observation recherchée

Voir si la concurrence **faim vs soif** provoque spontanément :

- départ des plantes campées ;
- trajets nourriture <-> eau ;
- concentration autour de certains points d'eau ;
- surexploitation locale ;
- périodes de faible croissance ;
- pénuries d'eau accessible malgré une eau totale constante.

Aucun de ces phénomènes ne doit être programmé explicitement.

## Modèle Codex

Règle permanente : avant chaque délégation, le pilote recommande modèle + niveau de reasoning.

Pour l'implémentation de #2 :

**GPT-5.6 Sol — High reasoning**

Motif : changement HIGH-RISK touchant une quantité conservée, plusieurs transferts couplés, le comportement animal, la croissance végétale et l'ordre global de simulation.
