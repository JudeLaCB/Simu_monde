# Monde VJ — Couche 20.5.2 : nuages stratifiés

Prototype autonome HTML — ouvrir [Monde VJ couche 20.5.2](Monde_VJ_Atlas_3D_Couche_20_5_2_Nuages_Stratifies.html) dans Chrome ou Edge.

## Principe
Le moteur conserve ses six stocks physiques de nuages `atm20Cloud[k*SIZE+i]`. **Le nouveau rendu utilise directement chaque strate**, sans les fusionner à une altitude moyenne. Altitudes terrain-suivantes : 0–50, 50–200, 200–500, 500–1000, 1000–2000, 2000–4000 m.

Pour chaque strate, le condensat est moyenné spatialement, puis lissé dans le temps **seulement à l'affichage**. Densité et opacité dépendent de la masse du niveau, sans normalisation par le poids initial historique. Une strate sans condensat ne crée pas de nuage. Les épaisseurs graphiques sont bornées par la tranche représentée. Les frontières visuelles restent périodiques.

Un bouton **☁ Vue strates** déplace la caméra pour inspecter la superposition, et un second clic revient au paysage. Les anciens rendus fusionnés restent dans les paramètres avancés.

## Physique
Rien n'est modifié dans les équations, les réserves, les bilans ou les flux de la couche 20.5.1. Sont préservés : les six niveaux atmosphériques, pluie en transit, évapotranspiration, cycle de la neige, sols/nappes, vents périodiques et budgets climatiques. La faune reste suspendue.

## Limites
Le rendu reste un assemblage de sprites doux projetés sur un Canvas 2D, et **non un volume nuageux 3D à occlusion exacte**. Il existe une répartition historique initiale artificielle des condensats entre niveaux ; ce chantier ne la recalcule pas. Les tranches sont terrain-suivantes, pas une classification réelle des types de nuages. Des nuages élevés peuvent sortir du champ de la caméra de relief.

Voir [PROGRESS.md](PROGRESS.md) pour les tests ; les essais GPU Windows matériels et les durées multi-journées restent ouverts.
