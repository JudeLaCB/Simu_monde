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


## Versions supplémentaires sur cette branche

- **V2.3 — [Reconnaissance des paysages](v2_3_paysages.html)** : classification indicatrice des lacs, marécages, montagnes, vallées, plateaux et plaines par état local et composantes connexes. La lecture géographique ne modifie pas les équations hydrologiques.
- **V2.4 — [Cycle jour / nuit](v2_4_jour_nuit.html)** : 1 000 pas par jour, dont 500 éclairés ; température globale de l'atmosphère et température de sol par cellule ; chauffage solaire progressif, échanges thermiques sol/air et voisins, refroidissement radiatif et évaporation dépendante de la température.

## Bilans et limites de V2.4

- `W_total = W_surface + W_sol + W_atmosphere` demeure constant.
- `E_comptabilisée = E_gravitationnelle + E_sensible_sol_air + E_latente + E_solaire_restante + E_rayonnement_sortant` demeure constante dans le **système de comptabilité élargi**.
- Le Soleil est un réservoir fini d'énergie initiale ; quand celui-ci est épuisé, le jour continue d'être annoncé par l'horloge mais n'apporte plus de chaleur. Le rayonnement thermique est conservé comme énergie émise, sans être réinjecté artificiellement.
- L'horloge est `1000 pas = 24 h`; les coefficients d'écoulement et d'évaporation par pas sont des approximations, **pas** une hydrodynamique ni un modèle atmosphérique calibrés. L'évaporation maximale par défaut est passée de `0.15 mm/pas` (V2.3) à `0.004 mm/pas` pour permettre un bilan latent et thermique cohérent avec les ordres de grandeur de la nouvelle journée.
- Pas encore de pluie, condensation, vent, nuages ni conduction verticale dans le sol.
- Le core Python historique sous `src/` n'est pas modifié : les prototypes restent des fichiers HTML autonomes.
- Tests manuels automatisés dans Chromium : 2 000 pas sur configuration standard, reproductibilité exacte après reset, contrôles de masse et d'énergie, variantes de rayonnement/évaporation, vue des températures et mise en page mobile.
