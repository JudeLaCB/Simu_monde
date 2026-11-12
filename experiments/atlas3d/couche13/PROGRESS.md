# Monde VJ — Couche 13 : météorologie dynamique (Atlas 3D)

> Branche expérimentale isolée de la simulation 2D historique. Le pilote 3D est un HTML autonome ; ce dossier conserve les décisions, preuves et limites. **Le prototype HTML est livré séparément dans la conversation, pas encore versionné ici.**

## Décisions validées — 12 novembre 2026

- **2 000 pas = 24 h simulées**, soit **43,2 s/pas**.
- Herbivores introduits au **pas 4 000** et carnivores au **pas 6 000**, pour conserver les jalons en jours simulés.
- Couche 13 limitée aux neuf chantiers approuvés : horloge, calibrage écologique et hydrologique, régimes persistants, rotations/rafales, brises thermiques, couplage climat, tableau de bord et validation.
- Préserver la carte 2 × 2 km, les nuages de la couche 11 et la pluie fusionnée de la couche 12 ; ne pas confondre les régimes synoptiques heuristiques avec un solveur de pression 3D.

## Avancement (en cours)

- [x] Reprise du prototype standalone couche 12.
- [x] Remplacement des constantes d'horloge et recalibrage des principaux flux par pas (facteur 0,5).
- [x] Météo régionale seedée : régimes persistants de 2–7 jours et interpolation progressive.
- [x] Brises locales des pentes jour/nuit ; champ local déjà raccordé au transport nuage/pluie.
- [x] Interface de choix dynamique/manuel, variabilité, brise, bulletin.
- [x] Vérification de syntaxe JavaScript ; ouverture sous Chromium, 20 pas sans erreur de page.
- [ ] Simulation longue jusqu'aux apparitions des deux populations et vérification des invariants.
- [ ] Vérification de reproductibilité et de continuité aux limites de régimes.
- [ ] ZIP Windows, rapport final des tests et validations visuelles.

## Invariants à surveiller

- Conservation de l'eau totale, énergie (y compris les réserves et puits de bilan) et matière sèche.
- Pas de nouvel apport de masse par le vent ou les régimes météorologiques.
- Même seed et mêmes paramètres => même trajectoire météorologique.
- Les réglages de visualisation des nuages et de la pluie ne modifient pas les réservoirs.

## Risques et limites

La météo régionale est imposée par une loi temporelle stochastique déterministe (seed), **pas** par un solveur des équations primitives. Les vitesses de transport sont données en cellules/pas, pas en m/s mesurés. Les changements de cadence peuvent modifier des détails de comportement neuronaux malgré le recalibrage des flux.
