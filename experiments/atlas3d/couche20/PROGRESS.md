# Couche 20 — Journal de développement

**13 novembre 2026** · branche `prototype/couche-20-atmosphere-stratifiee` depuis couche 19, sans fusion vers `main`.

## Implémenté
- [x] Six niveaux atmosphériques terrain-suivants (0–4 km), 240 000 cellules, stockage séparé vapeur/nuages.
- [x] Échanges avec végétation et sol injectés dans la première tranche, conservation stricte par colonne.
- [x] Transport horizontal conservatif et cisaillé par altitude, tous les 8 pas.
- [x] Transfert vertical borné entre couches ; mélange lié au soulèvement et à l'ensoleillement.
- [x] Condensation, réévaporation et précipitation par couche ; pluie ou neige selon température de surface.
- [x] Correction du potentiel gravitationnel des réservoirs atmosphériques.
- [x] Inspecteur des six niveaux par clic sur le terrain ; température, pression indicative, vent, vapeur, nuages.
- [x] Interface simple et 7×7 configurations conservées ; aucune modification du traitement des animaux (en pause).
- [x] Moteur historique disponible en désactivant le nouveau module, pour comparaison A/B.

## Tests
- `node --check` : valide.
- Montagnes + seed 42 : 250 pas chacun en tempéré, polaire et tropical, erreurs relatives eau/énergie/matière sèche **inférieures à 1e-14**, aucune erreur JS.
- **Montagnes + tropical + seed 42, 2 000 pas consécutifs :** erreur eau **6.40e-15**, énergie **1.46e-15**, matière sèche **0**. Pluie cumulée 17,86 M kg ; activité cumulée de mélange vertical 12,39 M kg (somme des flux absolus, pas débit net). Pas d'alerte ni erreur JavaScript.
- Régression moteur vertical désactivé : égalité stricte des tableaux eau, vapeur, nuages et nappes et des bilans avec couche 19, après 150 pas (Mixte/Tempéré/seed 42).
- WebGL2 / Chromium-SwiftShader : rendu validé à 120 pas, aucune erreur JS, coupe verticale six lignes. Canvas testé aussi.

## Périmètre encore ouvert — couche 20.2
- Énergie thermique stockée indépendamment par niveau et cellule (au lieu d'un profil diagnostique sur `airHeat` global).
- Dynamique atmosphérique couplée à la pression et à la masse d'air sec ; pas de Navier–Stokes / équations primitives pour l'instant.
- Chute de pluie et neige à travers les niveaux, avec possibilité de réévaporation intermédiaire.
- Rendu nuageux multi-altitude en vraie géométrie 3D et tests GPU matériel Windows multi-jours.

Ceci est un **prototype de basse troposphère stratifiée avec transport conservatif**, pas encore un modèle atmosphérique tridimensionnel complet.

[HTML autonome](Monde_VJ_Atlas_3D_Couche_20_Strates_Atmospheriques.html) · [Guide](README.md)
