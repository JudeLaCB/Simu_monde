# Couche 20.4 — Rapport d'implémentation

**Statut : prototype intégré, tests ciblés et 2 000 pas en climat tempéré validés.** Branche `prototype/couche-20-4-cycle-eau`, issue de `fix/couche-20-3-nuages-stables`, **sans modification de main**.

## Livré
- [x] Température et énergie thermique indépendantes par strate sur 240 000 cellules atmosphériques.
- [x] Mélange vertical conservatif et échanges sol/air locaux ; bilan de chaleur global synchronisé.
- [x] Dépendance non linéaire de la condensation à la température, normalisée sur les stocks météorologiques du prototype.
- [x] Pluie et neige en transit par strate (comptabilisées dans les bilans), réévaporation et fonte pendant la chute.
- [x] Évaporation et transpiration modulées par humidité et vent.
- [x] Altitudes visuelles des nuages selon leur niveau de masse condensée et relief lissé, plus de base globale définie à partir du sommet maximal.
- [x] Maintien du rendu fusionné et stable de 20.3, frontière atmosphérique périodique, rivières/nappes fermées.
- [x] Contrôles de positivité pour la pluie et la neige en transit ; erreurs numériques fatales toujours détectées.
- [x] Node.js : script syntaxiquement valide.
- [x] **2000 pas continus** sous Mixte/Tempéré/seed 42 ; masse 3,4846e-15 ; énergie 6,6449e-16 ; matière sèche 0. Précipitations au sol 1,2246 M kg ; 4,43 t encore en transit au pas 2000.
- [x] Montagnes/Tropical/seed 42 : 150 pas ; masse 6,525e-15 ; énergie 7,969e-16. Précipitations formées 2,578 M kg ; arrivée au sol 2,463 M kg ; évaporées en vol 0,102 M kg.
- [x] Hautes montagnes/Polaire/seed 42 : 120 pas ; masse 4,035e-15 ; énergie 7,985e-16 ; neige et transit gelé non nuls.
- [x] WebGL2 activé sous Chromium/SwiftShader : 120 pas, aucune erreur JavaScript.

## Limites / prochaines actions
- [ ] Calibrer l'échelle absolue de saturation, les capacités d'air et les échangeurs de chaleur sur une référence climatique.
- [ ] Résoudre dynamiquement masse d'air sec et pression, transport horizontal de chaleur et dérive des gouttes.
- [ ] Tester plusieurs jours continus en climats tropical, polaire et sécheresse avec GPU Windows matériel.
- [ ] Vérifier les profils thermiques verticaux et les précipitations avec des observations ; les bilans sont une condition nécessaire, pas suffisante.

**Code :** [HTML autonome](Monde_VJ_Atlas_3D_Couche_20_4_Cycle_Eau.html).
