# Couche 20.5.2 — Rapport d'avancement

**Statut : prototype graphique terminé ; 15 novembre 2026.** Branche `fix/couche-20-5-2-nuages-stratifies` issue de `fix/couche-20-5-1-capacite-sol`, sans modification de `main`.

## Livré
- [x] Rendu doux à **six altitudes correspondant aux six niveaux simulés**.
- [x] Densité visuelle fondée sur les kg de condensat de chaque strate ; niveaux vides non dessinés.
- [x] Lissage horizontal périodique par niveau et lissage temporel uniquement graphique.
- [x] Épaisseur de chaque masse plafonnée par la hauteur de sa strate.
- [x] Bouton « Vue strates » réversible ; rendu fusionné 20.3 toujours disponible.
- [x] Aucune modification des équations hydrologiques, aérologiques ou des bilans de conservation.
- [x] JavaScript syntaxiquement valide (`node --check`).
- [x] Tests Chromium Canvas : tropical (40 pas), polaire (50 pas), tempéré (100 pas).
- [x] Test WebGL2/SwiftShader : tropical (10 pas), six niveaux présents, aucune erreur JavaScript.

## Mesures
- Montagnes + tropical + seed 42, pas 40 : **490 635,17 kg de nuages** ; répartition selon six couches (92 061, 123 757, 108 915, 83 519, 54 700 et 27 684 kg). Erreurs relatives masse 2,52e-15 et énergie 6,64e-16, strictement égales à la couche 20.5.1, ainsi que l'eau et le vent.
- Montagnes + polaire + seed 42, pas 50 : masse erreur 4,28e-15 ; énergie 5,32e-16 ; nuages détectés dans six tranches.
- Montagnes + tempéré + seed 42, pas 100 : aucun nuage affiché dans les six niveaux, et aucune valeur inventée par le rendu ; masse erreur 2,93e-15.
- Chromium WebGL2/SwiftShader au pas 10 : 6 niveaux actifs, sans erreur.

## Limites et suites
- [ ] Valider les occultations nuage/terrain (overlay Canvas sur une scène WebGL).
- [ ] Recalibrer la distribution historique de condensat pour que les types de couches émergent mieux des températures et stabilités, plutôt que des poids initiaux.
- [ ] Tests de performance / 2 000 pas, GPU Windows matériel.

Les six strates sont déjà des réservoirs physiques depuis la couche 20 ; **ce changement concerne leur représentation**, pas leur mécanisme de formation.
