# Monde VJ — Couche 16 : nappes phréatiques

Prototype standalone géomorphologie/écosystème (étape 16), hérité de la couche 15.1.
- [HTML hors-ligne](Monde_VJ_Atlas_3D_Couche_16_Nappes_Phreatiques.html)
- [Rapport de développement et de tests](PROGRESS.md)

## Démarrage
Ouvrir le HTML dans Edge ou Chrome sur Windows. Aucun serveur ou paquet n'est nécessaire.

## Contenu
- Aquifère libre par cellule de 10×10 m, avec substratum, épaisseur, rendement spécifique et conductivité procédurale.
- Histoire hydrologique *héritée* : 42 % de la masse d'eau initiale (réglable) passe de la surface à la nappe selon les vallées et les chenaux ; **aucune masse supplémentaire créée**.
- Recharge lente depuis un sol humide, écoulement latéral de type Darcy à frontières closes, échanges bidirectionnels rivière–nappe, résurgences vers les lits exposés, petite remontée capillaire vers la zone racinaire.
- Mini-cartes profondeur, saturation et perméabilité, télémétrie et export CSV étendu.
- Le relief de la couche 15 reste figé après génération ; météo de couche 13, rivières de 14 et pluie 3D avec occlusion de 15.1 conservées.
- Animaux toujours désactivés et horloge de 2 000 pas/jour.

## Modèle mathématique
Charge libre `H_i = z_base_i + q_i / Sy_i` où `q_i` est l'eau équivalente (m), et `Sy_i` le rendement spécifique (sans unité). Flux de Darcy simplifié entre voisins, en mètres d'eau équivalents, limité par les capacités et les stocks. Énergie gravitationnelle de chaque nappe ajoutée au bilan.

## Validation
Une journée complète (2 000 pas) vérifiée ; contrôle de masse, énergie et matière sèche sous 2e-14. Quatre seeds supplémentaires vérifiées jusqu'à 120 pas. Désactivation du module : correspondance exacte à la couche 15.1 après 0, 140 et 500 pas. Reset avec seed identique reproduit le stock initial octet par octet. Rendu WebGL2 vérifié dans Chromium / SwiftShader.

**Limites :** propriétés hydrogéologiques synthétiques non calibrées ; pas de géologie multicouche, de nappe captive, d'historique climatique réel ni de conditions aux limites ouvertes. Une simulation continue à 6 000 pas n'a pas été validée dans le banc d'essai : son navigateur ralentit nettement au-delà de 2 000 pas.
