# Monde VJ — Couche 20.5 : journal de développement

**Statut : prototype livré et testé sur des scénarios ciblés.** Branche `prototype/couche-20-5-budgets-hydriques-climatiques` issue de la couche 20.4, sans fusion dans `main`.

- [x] Budget hydrique total initial propre aux 7 climats, distinct de la distribution des eaux du paysage.
- [x] Facteur appliqué une fois au générateur initial, avant le stockage dans les aquifères, la neige et l'atmosphère.
- [x] Suppression de la limite minimale de volume sur le littoral, incompatible avec un climat aride.
- [x] UI : budget relatif au changement de climat ; masse réelle du système après génération ; Random Seed préservé.
- [x] Mode avancé indépendant : quand l'utilisateur régénère manuellement, facteur automatique remis à ×1.
- [x] Relief identique sur 7 profils, même seed 42 et paysage Montagnes.
- [x] Bilan initial conservé dans les 7 profils.
- [x] 110 pas tempéré / aride / sécheresse : conservation <1e-13.
- [x] 15 pas tropical : conservation de masse ≈3e-15 et d'énergie ≈3e-16.
- [x] Côte/seed 42 : masse initiale 13,4 Md kg en tempéré ; 2,144 Md kg en aride ; 1,34 Md kg en sécheresse.
- [x] HTML autonome et archive Windows testée pour intégrité.
- [ ] Tester plusieurs journées tropicales (un test prolongé s'est interrompu par limite de ressources du navigateur), polaires et sèches sur GPU matériel.

Les coefficients ne sont pas calibrés sur une région réelle. Ils désignent des **conditions initiales hydrologiques héritées**. La masse doit être conservée au sein de chaque simulation fermée mais peut différer entre générations de climats.
