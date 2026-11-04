# Monde VJ — Prototypes autonomes d'environnement

Ces fichiers HTML sont des expériences indépendantes du moteur Python `src/simu_monde/core`. Ils se lancent sans installation, dans un navigateur moderne. Ils préparent une éventuelle migration des lois environnementales dans le moteur principal.

## Versions

- **V2.1b — [Reliefs localisés, massifs et bassins](v2_1b_reliefs_localises.html)** : état de référence, conservé tel quel dans `main` (commit `41506a8`). Terrain procédural reproductible, eau de surface finie, écoulement gravitationnel dissipatif, conservation de l'eau et bilan d'énergie simplifié.
- **V2.2 — [Évaporation et rétention](v2_2_evaporation_retention.html)** : ajoute le stockage local d'eau dans le sol et un réservoir atmosphérique, sans retirer ou modifier V2.1b.

## Règles nouvelles de V2.2

- **Infiltration** : maximum 12 mm d'eau équivalente par cellule et par pas, limité par l'eau de surface et la place encore disponible dans le sol.
- **Capacité de rétention** : curseur 0–100 %, représentant une capacité de stockage par cellule comprise entre 0 et 0,8 m d'eau équivalente. C'est une *capacité*, et non un coefficient de ruissellement ou un taux de réémission.
- **Évaporation** : curseur 0–1 mm/pas pour l'eau de surface exposée ; si la surface est sèche, le sol humide peut évaporer à 35 % de cette vitesse. Les taux sont volontairement accélérés pour observer des changements en quelques centaines de pas (1 pas = 1 seconde simulée) et ne constituent pas une loi climatique calibrée.
- **Atmosphère** : réservoir de masse global qui reçoit toute l'eau évaporée. **Pas encore de condensation, de pluie, ni de mouvement spatial de vapeur**.
- **Énergie** : l'écoulement et l'infiltration dissipent l'énergie gravitationnelle en chaleur ; l'évaporation utilise une **réserve thermique initiale finie** et transfère de l'énergie vers une réserve latente. La gravité de la vapeur est comptée à une altitude de référence simplifiée. Ce modèle est un bilan comptable explicite, **pas** un modèle thermodynamique ou météorologique validé.

## Bilans

```text
W_totale = W_surface + W_sol + W_atmosphere = constante

E_totale = E_potentielle_gravitationnelle + E_thermique + E_latente = constante
```

Les valeurs sont vérifiées numériquement à chaque pas. L'énergie thermique ne peut pas être puisée indéfiniment : quand elle est insuffisante, l'évaporation s'arrête.

## Comparaisons à réaliser

1. Seed 42, 30 % d'eau, relief « Massifs et lacs », rétention 60 %, évaporation 0,15 mm/pas : observer l'eau de surface, du sol et de l'atmosphère après 500 pas.
2. Sur V2.2, choisir **0 % de rétention et 0 mm/pas d'évaporation** : la trajectoire d'eau de surface reproduit exactement V2.1b pour des paramètres initiaux identiques.
3. Tester indépendamment la rétention seule et l'évaporation seule pour identifier leurs effets.

## Frontière d'architecture

Ces prototypes n'implémentent ni organismes, ni pluie, ni eau souterraine mobile, ni minéraux. Aucun code de l'ancien simulateur écologique n'est modifié par leur ajout. Le futur système d'environnement Python doit préserver le monde en mètres, la seed, le pas de temps fixe, l'indépendance du rendu et les tests d'invariants.
