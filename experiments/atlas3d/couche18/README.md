# Monde VJ — Couche 18 : système Terre et cryosphère

**Version HTML autonome sur Windows** : [ouvrir le prototype](Monde_VJ_Atlas_3D_Couche_18_Systeme_Terre.html).

## Couche 18A — Socle des cinq sphères
Cinq composants logiques : atmosphère (vapeur, nuages), hydrosphère (surface, sol, nappes), géosphère (relief et roches fixes), biosphère (végétation ; animaux en pause) et cryosphère (neige et glace). Les nouveaux stocks sont intégrés aux **bilans de masse et énergie existants**, sans double comptage. Les solveurs sont encore assemblés dans un seul HTML, et non encore scindés en cinq modules de code.

## Couche 18B — Neige, gel et fonte
- Réservoirs `snowWater18` et `surfaceIce18`, en mètres d'eau équivalente par cellule.
- Neige depuis les nuages sous conditions froides, gel de l'eau libre et fonte vers le réservoir liquide.
- Chaleur latente de fusion de 334 kJ/kg portée par un bilan `phaseEnergy18` explicitement conservé, et chaleur sensible compensatrice.
- Nouveau profil simplifié **Montagnes enneigées**, avec état enneigé hérité d'un hiver passé et nuages initiaux : ce stock provient **exclusivement de l'eau de surface existante**.
- Affichage WebGL2/Canvas des zones enneigées, surface de lac glacée, mini-carte `Neige et gel (stock)`, statistiques neige, gel et fonte.
- Les six paysages précédents, l'interface simple, le relief, les rivières, les nappes, la pluie 3D et le vent dynamique sont préservés. 2 000 pas/jour ; faune en pause.

## Essais
- Node.js : syntaxe JavaScript valide.
- Chromium Canvas et WebGL2 SwiftShader : shaders et interface validés, aucune erreur JavaScript.
- Tests **2 000 pas continus** : mode mixte tempéré et mode enneigé seed 42, séparément, erreurs eau/énergie/matière sèche < 1e-14.
- Après 2 000 pas enneigés : neige 41,93 M kg, glace 0,026 M kg, chutes de neige cumulées 2,48 M kg, gel cumulé 8,56 M kg, fonte cumulée 10,68 M kg.
- Régression avec la couche 17 en mode mixte seed 42 à pas 200 : tableaux de réservoirs et végétation, énergie et masse **strictement identiques**.
- Seeds 1, 72026 et 98765 : conservation vérifiée sur 100 pas.

## Limites
- Modèle pédagogique de gel/fonte, pas de dynamique des glaciers, de saisonnalité réelle, de transfert de neige par le vent ni d'équations tridimensionnelles d'atmosphère.
- Conditions hivernales imposées par le profil, pas calculées à partir d'une année météorologique.
- Cryosphère sans couplage au gel profond des sols et sans albédo rétroactif.
- La géosphère est fixe pendant l'évolution de 2 000 pas/jour ; brancher un modèle tectonique n'est pas requis.
- Tester les performances GPU Windows sur plusieurs jours avant toute fusion dans `main`.
