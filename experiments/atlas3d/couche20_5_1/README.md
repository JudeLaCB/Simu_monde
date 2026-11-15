# Monde VJ — Couche 20.5.1 : retour d'eau des plantes et sol saturé

[Ouvrir le HTML autonome corrigé](Monde_VJ_Atlas_3D_Couche_20_5_1_Capacite_Sol.html).

## Incident reproduit

Message utilisateur : `Physique 20.1 — pas 9429, après calcul : sol[1248]=0.6400133340871083 hors [0, 0.6400001]`.

Cause : `stepPlantHydrology()` rendait toute l'eau stockée dans une plante devenue quasi absente au sol sans vérifier la capacité encore disponible. Contrairement à l'infiltration et à la remontée capillaire, ce transfert n'était pas borné.

Au pas 9429 simulé par un banc de test instrumenté, avec la cellule 1248 préremplie presque à 0,64 m et une plante détentrice de 1,334 kg d'eau :
- Ancienne 20.5 : `sol[1248]=0.6400128539157284`, contrôleur interrompant le calcul.
- Nouvelle 20.5.1 : `sol[1248]=0.64`, surplus transféré à l'eau de surface, simulation poursuivie.
Ce test reproduit **la signature de l'erreur**, pas la totalité des 9429 pas historiques (seed et climat originaux inconnus).

## Correctif

La fonction `returnDeadPlantWater20_5_1(i)` renvoie au sol uniquement l'eau qui tient dans sa capacité. L'excédent devient une profondeur d'eau de surface `water[i]`, sans créer ni supprimer d'eau. La différence d'énergie potentielle gravitationnelle de cette eau libre est retranchée du stock thermique `airHeat`. Le contrôleur de sûreté et sa tolérance `1e-7` sont **inchangés**.

## Tests de validation

- `node --check` : JavaScript valide.
- Trois retours d'eau synthétiques (sol presque saturé, avec/sans eau libre) : réservoir sol borné, énergie et masse globales invariantes.
- Comparaison ancienne/nouvelle à la date artificielle du pas 9429, cellule 1248 : arrêt ancienne version, passage nouvelle version.
- Scénarios **200 pas** en `Mixte / seed 42` sous les climats Tempéré, Sécheresse, Aride, Polaire : aucune alerte, écarts relatifs masse/énergie/matière sèche inférieurs à `1e-9`.
- Les tests complets continus jusqu'à 9429 pas avec les réglages exacts de l'utilisateur et WebGL2 matériel Windows **restent à effectuer**.

Le cycle de l'eau, les budgets climatiques 20.5, le vent périodique, les strates, la cryosphère, le relief et la faune suspendue ne sont pas modifiés. Il n'existe pas encore de système de sauvegarde/reprise du monde : une nouvelle version nécessite de régénérer la seed et les paramètres d'origine.

Le ZIP Windows, les deux JSON de test et les scripts Playwright de reproduction sont livrés dans la conversation.
