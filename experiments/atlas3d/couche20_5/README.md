# Monde VJ — Couche 20.5 · Budgets hydriques climatiques

Prototype autonome : [HTML à ouvrir dans Chrome ou Edge](Monde_VJ_Atlas_3D_Couche_20_5_Budgets_Hydriques_Climatiques.html). Le ZIP Windows contenant l'HTML, une capture et les tests est fourni dans la conversation.

## Choix de modélisation

Le *paysage* garde la topographie et la répartition de référence des réservoirs. Le *climat* multiplie le **budget d'eau initial total** avant la redistribution vers nappes, cryosphère et atmosphère. Pas de source ou perte d'eau créée pendant la simulation. Pour paysage et seed identiques, le terrain est identique.

| Climat | Fraction d'eau initiale de référence |
| --- | ---: |
| Tempéré | 100 % |
| Aride / désertique | 16 % |
| Tropical humide | 160 % |
| Mousson | 135 % |
| Polaire | 75 % |
| Sécheresse intense déjà installée | 10 % |
| Méditerranéen | 65 % |

**Ces fractions sont des choix procéduraux et non des vérités hydrologiques universelles.** Une sécheresse de courte durée ne devrait pas supprimer la masse initiale d'eau : le mode choisi ici représente une sécheresse *prolongée* préexistante. Dans le mode littoral, le minimum d'eau forcé a été supprimé pour que la carte puisse être côtière et sèche. Le littoral conserve des frontières fermées, pas un océan réel.

Le menu simple affiche le budget relatif et la masse d'eau initiale exacte après génération. L'option avancée « Régénérer » désactive le facteur climatique et permet de fixer directement la quantité d'eau.

## Conservation de l'existant

2 × 2 km, 200 × 200 cellules, 2 000 pas/jour, six niveaux atmosphériques, pluies en transit, évapotranspiration, rendu de nuages doux, atmosphère périodique, sols, rivières, nappes, neige, végétation et faune en pause.

## Validation

Voir [PROGRESS.md](PROGRESS.md). JavaScript Node.js valide. Test sous Chromium : les sept profils climatiques pour Montagnes/seed 42 ont exactement le même relief et les masses totales annoncées, sans alerte au pas 0. Tempéré, aride et sécheresse : 110 pas, erreurs de masse et d'énergie <1e-13. Tropical : 15 pas validés, test plus long interrompu par le navigateur, non compté comme réussi. Bord de mer : rapport de masse 100/16/10 % confirmé pour tempéré/aride/sécheresse. Le rendu WebGL2 matériel Windows et les tests de plusieurs journées sont encore ouverts.
