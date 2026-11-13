# Journal d'avancement — Couche 16 · nappe phréatique

**Statut : prototype terminé, version expérimentale.**
**Date : 13 novembre 2026.**
**Branche :** `prototype/couche-16-nappes-phreatiques`.
**Origine :** couche 15.1 (pluie occultée).

## Tâches

- [x] Maintenir 200×200 cellules (2×2 km), 2 000 pas/jour et faune en pause.
- [x] Ajouter substratum, puissance aquifère, rendement spécifique et conductivité à partir du relief et d'une roche spatiale seedée.
- [x] Initialiser une nappe déjà formée **par redistribution de l'eau initiale** ; 42 % par défaut, sans créer de masse.
- [x] Permettre le transfert d'eau sol non saturé → nappe lorsque le seuil de recharge est atteint.
- [x] Implémenter un échange Darcy D4 à pas souterrain de 10 ticks (432 secondes de simulation par sous-cycle).
- [x] Gérer rivières perdantes et sources dans les lits exposés lorsque la nappe affleure.
- [x] Ajouter une remontée capillaire lente à moins de 1,8 m du sol.
- [x] Ajouter énergie potentielle souterraine et utiliser les variations comme chauffage de bilan ; conserver masse/dry energy.
- [x] Ajouter mini-cartes profondeur/saturation/conductivité, inspection par cellule, compteurs et export CSV.
- [x] Tester et fournir le HTML et le ZIP Windows hors ligne.

## Mesures validées

- Au pas 0, seed 42, 42 % du budget initial de **2,600 Md kg** est stocké en nappe, soit **1,092 Md kg**.
- À 2 000 pas : nappe ≈ **1,284 Md kg** dans le dernier essai avec capillarité et contact rivière ; eau totale **2,600 Md kg** ; erreurs relatives masse ≈ 1,3e-15, énergie ≈ 4e-16 et matière sèche ≈ 5e-16.
- Recharges, transferts latéraux, échanges avec les rivières et remontées capillaires non nuls ; aucun volume négatif ni dépassement de capacité.
- Moteur nappe désactivé : parité exacte des tableaux eau, nuages, végétation et principales métriques aux pas 0, 140 et 500 par rapport au HTML couche 15.1.
- Quatre seeds (1, 42, 72026, 98765) contrôlées pendant 120 pas, bilans stables.
- Test de reproductibilité : même tableau souterrain initial pour même seed après réinitialisation.
- Test contrôle « recharge = 0, contact rivière désactivé » : recharge et pertes/résurgences nulles, Darcy toujours actif.
- WebGL2 / SwiftShader : démarrage et rendu sans exception JavaScript, test 800 pas.

## Modèle et limites

- Approche d'une **nappe libre 2D** (une couche d'aquifère par cellule) ; `gwWater` exprimé en mètres d'eau équivalents.
- Loi Darcy discrète approximative avec rendement spécifique, transmissivité locale et limitation des stocks ; le modèle de rivière existant ne mesure pas encore les débits 1D.
- La répartition initiale n'est **pas une simulation des précipitations passées pendant des siècles** ; c'est un état hérité de recharge topographique plausible.
- Aucune nouvelle masse d'eau. Bord du domaine fermé ; pas de nappe captive, de géochimie, de couplage thermique souterrain indépendant ou de porosité temporelle.
- Banc d'essai Chromium : simulation continue validée jusqu'à 2 000 pas ; essai plus long interrompu par une limite de temps/ressources, non interprété comme une validation des états postérieurs.
- Pas de merge dans `main` ; tests matériels Windows recommandés avant fusion.

**Fichiers :** [HTML autonome](Monde_VJ_Atlas_3D_Couche_16_Nappes_Phreatiques.html) et [README](README.md).
