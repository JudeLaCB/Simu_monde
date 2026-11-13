# Couche 15 — Générateur géomorphologique

Ouvrir [le prototype HTML corrigé (15.1)](Monde_VJ_Atlas_3D_Couche_15_Relief_Geomorphologique.html) dans Chrome ou Edge.

Nouvelle génération : **dorsales montagneuses connectées + crêtes secondaires + résistance rocheuse spatiale + érosion ancienne D4**. Tout est exécuté avant la création du monde humide et de son bilan énergétique. Le modèle de rivières de la couche 14, la météo de la couche 13 et l'horloge 2 000 pas/jour restent en place. Les animaux sont temporairement désactivés.

## Utilisation
Dans « 15 / Géomorphologie et histoire du terrain », choisir le générateur géomorphologique ou l'ancien générateur de dômes. Régler la morphologie **alpin / ancien / plateau / mixte**, l'importance des crêtes, l'intensité de l'érosion ancienne et le contraste des roches. Appuyer sur **Régénérer** pour appliquer ces choix. Le mode mini-carte « Érosion ancienne et roches » indique les différences spatiales ; l'autre mode « Réseau hydrographique » montre les lits secs/en eau.

## Vérification
Voir [PROGRESS.md](PROGRESS.md). Les tests portent sur 4 seeds, 4 profils, comparaison A/B, invariants de matière/énergie, 2 000 pas continus, drainage D4 et absence de géologie pendant les pas physiques.

Ce prototype ne modélise pas la tectonique ou le transport sédimentaire en temps géologique réel. **Le réseau fluvial n'est pas un solveur hydraulique détaillé.** Rendu WebGL2 sur PC Windows à vérifier avant fusion.

**Pluie corrigée :** rendu WebGL2 avec occultation par relief/arbres/lacs (version 15.1), voir [le bilan](PROGRESS.md). Le mode Canvas a une occultation approximative.
