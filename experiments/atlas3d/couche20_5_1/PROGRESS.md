# Couche 20.5.1 — Journal du correctif

**15 novembre 2026 — correction ciblée du plafond d'eau du sol**, branche `fix/couche-20-5-1-capacite-sol` issue de la couche 20.5. Aucune fusion dans `main`.

- [x] Identifier l'écriture non bornée `soilWater[i]+=plantWaterKg[i]/CELL_MASS` lors de la disparition d'une plante.
- [x] Développer `returnDeadPlantWater20_5_1(i)` : sol saturé → eau de surface, avec compensation de potentiel gravitationnel dans `airHeat`.
- [x] Reproduire une erreur `sol[1248]` à `tickCount=9429` dans un scénario instrumenté ; vérifier passage après correction.
- [x] Tester 3 restitutions d'eau synthétiques : aucun dépassement, aucune perte d'eau ou d'énergie.
- [x] Vérifier 200 pas par climat sur Tempéré, Sécheresse, Aride et Polaire (Mixte, seed 42).
- [x] Conserver les sécurités physiques sans augmenter la tolérance.
- [ ] Reproduire les 9429 pas **consécutifs** avec les paramètres exacts de l'utilisateur (non communiqués).
- [ ] Tester GPU matériel Windows.

[HTML corrigé](Monde_VJ_Atlas_3D_Couche_20_5_1_Capacite_Sol.html) · [Explication du correctif](README.md)
