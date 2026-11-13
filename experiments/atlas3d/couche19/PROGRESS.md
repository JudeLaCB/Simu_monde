# Couche 19 — Rapport de réalisation

**13 novembre 2026**. Branche `prototype/couche-19-climats-independants` issue de `prototype/couche-18-systeme-terre`. Pas de fusion dans `main`.

## Terminé
- [x] Menu de paysage conservé : 7 morphologies.
- [x] Menu séparé de climat : 7 profils.
- [x] Seed aléatoire générée uniquement sur clic 🎲, affichée, copiable, sans régénération immédiate.
- [x] Génération indépendante et reproductible, paramètres avancés repliés.
- [x] Température initiale, pluie, vent, évaporation, rayonnement, historique de nappe et conditions biologiques adaptés au climat.
- [x] Humidité initiale tropicale et mousson transférée de l'eau existante et équilibrée en énergie.
- [x] Cryosphère couplée au profil polaire, sans l'imposer par le choix du paysage.
- [x] Tests des bilans et essais GPU logiciel, ZIP Windows livré.

## Tests mesurés

- Pour **Montagnes + seed 42**, les 7 climats génèrent un relief numériquement identique (somme de contrôle : 42 839 998,22 ; comparaisons effectuées sur le même tableau de terrain).
- À **160 pas chacun**, tous les climats ont des erreurs relatives eau, énergie, matière sèche <1e-14, aucune erreur JS. Précipitations et températures différenciées.
- Pour **Mixte + Tempéré, seed 42**, **2 000 pas continus**, erreurs de conservation : eau 2,57e-15 ; énergie 6,64e-16 ; matière sèche 1,69e-16. Faune 0.
- Régression couche 18 ↔ 19 après 200 pas sur Mixte + Tempéré seed 42 : égalité stricte pour eau, nuages, vapeur, nappes, plantes, température et bilans.
- WebGL2 via Chromium / SwiftShader : scénario polaire à 150 pas, aucune erreur.
- Générateur aléatoire : change la seed affichée sans toucher à la seed du monde déjà initialisé.

## Limites

Climats synthétiques non calibrés, alternance 20 jours pour mouisson et méditerranéen non astronomique. Les eaux initiales ne sont pas identiques entre climats (histoire hydrologique différente). Le littoral est fermé (pas d'océan réel). Le test de 2 000 pas a été réalisé en tempéré uniquement ; essai séquentiel de journées multiples interrompu par les ressources Chromium. Avant fusion dans main, valider matériellement sous Windows et réaliser d'autres journées indépendantes en profils extrêmes.

[HTML autonome](Monde_VJ_Atlas_3D_Couche_19_Climats_Independants.html) · [Guide](README.md)
