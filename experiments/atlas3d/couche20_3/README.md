# Monde VJ — Couche 20.3 : nuages doux et stables

**Correctif d'affichage exclusivement, issu de la couche 20.2.** Aucun calcul météorologique ou hydrologique n'est changé.

## Fonctionnement
- Par défaut, restitue le rendu fusionné de la couche 19 à partir de la **somme des six niveaux physiques**. Les six réservoirs de vapeur et nuages, le transport périodique, la pluie, les vents, le sol et les nappes sont conservés.
- Retire le décalage graphique `tickCount % 8` qui revenait brutalement à zéro au moment du transport physique, produisant des saccades.
- Lisse uniquement l'intensité visuelle du champ nuageux avec une moyenne temporelle exponentielle par pas simulé. Cette mémoire visuelle est réinitialisée à chaque régénération. Elle n'agit sur aucun bilan.
- Dans **Paramètres avancés > Réglages graphiques des nuages**, on peut réactiver le rendu **Trois bandes d'altitude · expérimental** ou les micro-nuages historiques pour comparaison.

## Vérifications
- Syntaxe JavaScript validée par Node.js.
- Chromium / Playwright (Canvas de secours) : zéro erreur JavaScript, seed 42, paysage montagne, climat tropical.
- Au pas 32, couche 20.2 versus 20.3 : masses de nuages physiques et d'eau, vent, bilans massique et énergétique **identiques**.
- Variation moyenne RGB entre les pas 7 et 8 sur le canevas nuageux : **2,76 → 1,30** (échelle 0–255). Indicateur d'amplitude, et non preuve de qualité subjective.
- Validation visuelle GPU Windows et essais multi-journées restent ouverts. L'audit physique 20.1 reste applicable.

**Fichier :** [HTML autonome](Monde_VJ_Atlas_3D_Couche_20_3_Nuages_Stables.html).
