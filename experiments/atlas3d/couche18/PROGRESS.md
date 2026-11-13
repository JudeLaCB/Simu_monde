# Couche 18 — Progression, arbitrages et validation

**Statut : prototype complet (18A + 18B), 13 novembre 2026.**  
**Branche :** `prototype/couche-18-systeme-terre` depuis `prototype/couche-17-interface-simplifiee`, **sans merge dans main**.

## Objectifs et statut
- [x] Conserver l'interface seed + choix paysage + Générer, en préservant les paramètres avancés repliés.
- [x] Déclarer un registre des cinq sphères et exposer un tableau de bord de leurs réservoirs.
- [x] Inclure cryosphère dans le bilan d'eau et d'énergie, sans nouveau budget d'eau arbitraire.
- [x] Ajouter neige issue des nuages, gel de surface et fonte en retour des rivières/lacs.
- [x] Déduire la chaleur de fusion/solidification des réservoirs d'énergie thermique ; compter l'énergie gravitationnelle de la neige et de la glace.
- [x] Ajouter l'initialisation d'hiver passé sur les cimes, financée par l'eau existante, ainsi qu'un champ nuageux hivernal initial.
- [x] Nouveau profil « Montagnes enneigées » et mini-carte cryosphère ; rendu neige et glace WebGL2 / Canvas.
- [x] Préserver les autres modes, la géomorphologie, la météo dynamique, la végétation et les nappes ; animaux suspendus.
- [x] Tests longue durée, seeds multiples, régression ancienne couche, rendu graphique et ZIP Windows.

## Résultats quantitatifs
Profil mixte seed 42 : 2 000 pas, erreurs relatives `mass=2.57e-15`, `energy=6.64e-16`, `dry=1.69e-16`. Aucune glace, neige ou précipitation neigeuse dans ce profil tempéré sur la durée testée.

Profil montagnes enneigées seed 42 : 2 000 pas, erreurs `mass=3.48e-15`, `energy=3.99e-16`, `dry=0`. Au départ, 41,6 M kg d'eau sont redistribués en neige héritée ; après un jour, environ 41,93 M kg de neige, 0,026 M kg de glace ; 2,48 M kg de neige précipitée, 8,56 M kg de gel et 10,68 M kg de fonte cumulés. Aucun déficit massique ni énergétique.

Régression parité couche 17 ↔ 18 : **égalité exacte** après 200 pas du profil mixte, seed 42, pour les réservoirs eau, sol, vapeur, nuages, biomasse végétale et bilans. Seeds 1 / 72026 / 98765 testées 100 pas chacune en mode enneigé, pas d'anomalies.

Rendu WebGL2 matériel logiciel sous Xvfb SwiftShader ; rendu Canvas de secours également testé. Script de syntaxe Node.js et tests Playwright fournis dans ZIP.

## Hypothèses scientifiques et techniques
La géosphère et la géologie restent fixes ; l'hydrosphère regroupe le réservoir d'eau liquide, la cryosphère les stocks gelés ; l'atmosphère contient vapeur/nuage ; la biosphère contient les plantes. Leur relation est suivie par bilan et flux à l'intérieur du même moteur HTML. **Ce n'est pas encore un couplage logiciel découplé entre cinq solveurs.**

Le scénario hivernal est imposé et ne constitue pas une prédiction météorologique. La couverture de neige est une hauteur d'eau équivalente, non une épaisseur géométrique de neige de densité variable. Pas encore de dynamique glaciaire, d'albédo rétroactif ni de saisonnalité annuelle. Conservation globale du système fermé vérifiée, mais les paramètres de phase et de climat ne sont pas calibrés sur un site réel.

## Fichiers
- [Prototype HTML](Monde_VJ_Atlas_3D_Couche_18_Systeme_Terre.html)
- [Guide](README.md)
- ZIP Windows avec lanceur, aperçu graphique et tests dans la conversation ChatGPT.
