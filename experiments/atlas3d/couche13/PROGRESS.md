# Monde VJ — Couche 13 : météo dynamique — bilan du prototype

**Statut : prototype standalone implémenté et testé (12 novembre 2026).**  
**Branche :** `prototype/couche-13-meteo-dynamique`. Ce développement 3D expérimental ne modifie pas le moteur 2D de `main`.

## Source versionnée

- [Ouvrir le HTML autonome de la couche 13](Monde_VJ_Atlas_3D_Couche_13_Meteo_Dynamique.html).
- Les livrables Windows (ZIP + aperçu) sont également fournis dans la conversation.
- Le code historique de la couche 12 a servi de base. Le HTML ne dépend pas d'un serveur ou de bibliothèques à télécharger.

## Décisions validées

- **2 000 pas = 24 h**, soit **43,2 s/pas**, à partir de la couche 13.
- Les herbivores naissent une fois au pas **4 000**, les carnivores au pas **6 000**.
- Aucune saison, aucun changement pluriannuel et aucun solveur synoptique 3D de pression dans cette couche.

## Les neuf chantiers approuvés

- [x] **C13.1 Horloge** : journée 2 000 pas, lever et coucher du soleil recalibrés, affichage.
- [x] **C13.2 Écologie** : cadence végétale, stress, dispersion, maturité, reproduction et vieillissement animaux recalibrés en jours simulés.
- [x] **C13.3 Flux physiques** : transport d'eau, infiltration, évaporation, énergie solaire, rayonnement, chaleur, condensation et pluie ramenés à la nouvelle durée par pas.
- [x] **C13.4 Régimes** : séquences seedées de types anticyclonique, dépressionnaire et transition, de 2 à 7 jours.
- [x] **C13.5 Vent régional** : direction / vitesse interpolées sur la frontière des régimes ; fluctuations courtes sans discontinuité angulaire.
- [x] **C13.6 Brises thermiques** : vents de pente montants le jour, descendants la nuit, ajoutés au vent synoptique local.
- [x] **C13.7 Couplage** : le champ de vent local existant pilote le transport de vapeur/nuages, les précipitations et l'orographie.
- [x] **C13.8 Tableau de bord** : mode dynamique / manuel, variabilité, activation des brises, jour, régime, direction, vitesse numérique et prochain changement.
- [x] **C13.9 Validation** : test JavaScript de syntaxe, rendu dans Chromium, test d'interface, simulation à 6 200 pas, invariants et déterminisme.

## Résultats observés — seed 42, réglages par défaut

| Pas | Herbivores | Carnivores | Eau (erreur relative) | Énergie (erreur relative) | Matière sèche (erreur relative) |
|---:|---:|---:|---:|---:|---:|
| 2 000 | 0 | 0 | 2,58e-15 | 5,32e-16 | 1,69e-15 |
| 4 000 | 50 | 0 | 1,80e-15 | 1,20e-15 | 2,70e-15 |
| 6 000 | 64 | 4 | 2,06e-15 | 1,73e-15 | 3,04e-15 |
| 6 200 | 67 | 4 | 3,61e-15 | 1,33e-15 | 2,70e-15 |

- Les 14 checkpoints ont passé le seuil d'invariant (< 1e-9).
- Le code est compatible Chromium en rendu Canvas de secours dans l'environnement de test, sans erreur JavaScript observée.
- Le vent est continu au changement de régime testé, et les sorties météorologiques pour une seed sont identiques après réinitialisation.
- Les commandes de variabilité, mode régional manuel et activation des brises ont été vérifiées.

## Limites connues et points à surveiller

1. Les régimes régionaux sont une approximation temporelle seedée, **pas** une simulation de pression. La vitesse donnée en cellules/pas est une vitesse numérique de transport, non une prévision instrumentale en m/s.
2. Les budgets sont conservés mais le comportement biologique ne doit pas être supposé identique à l'ancienne couche à temps réel égal : la cadence de décision neuronale est plus fine.
3. Les tests graphiques ont couvert le rendu Canvas de secours ; tester séparément WebGL2 matériel sur le PC Windows.
4. La couche 13 ne met pas en œuvre les saisons et n'entraîne pas la création d'eau aux frontières. Le mouvement atmosphérique reste périodique sur la grille.
5. Ne pas fusionner ce prototype autonome dans le cœur 2D historique sans décision d'architecture explicite.

**Suite proposée :** essais sur Windows, validation visuelle de l'évolution météorologique à 2–7 jours, puis décision produit avant tout merge.
