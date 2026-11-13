# Monde VJ — Couche 17 : interface simplifiée

**Statut : prototype terminé et testé — 13 novembre 2026.**

## Objectif
N'afficher que trois choix utiles : **paysage, seed, Générer**. Préserver l'intégralité des réglages spécialisés des 16 couches précédentes, repliés par défaut derrière **Paramètres avancés**. Conserver le moteur 3D/hydrologique existant et la faune en pause.

## Interface
- Six profils reproductibles : Mixte, Montagnes, Bord de mer, Plateaux, Collines, Vallées et lacs.
- Chaque profil charge plusieurs réglages **réels** (géomorphologie, relief, érosion ancienne, volume/répartition d'eau, météo, recharge et stock phréatique).
- Même (profil, seed) => même terrain, mêmes eaux initiales et même état des nappes.
- Le bouton `Générer le monde` restaure les réglages du profil avant réinitialisation au pas 0.
- Le panneau avancé conserve tous les anciens contrôles ; son bouton `Régénérer` applique la configuration manuelle, sans écraser les paramètres par un preset.
- Le littoral reste une **côte avec bassin fermé**, sans vraies conditions océaniques (marées, houle, salinité, eau sortante).

## Validation
- JavaScript : syntaxe validée par Node.js.
- Interface sous Chromium Canvas : 6 profils vérifiés, 0 erreur JS, altitudes et réseaux différents.
- Test seed 42 : bord de mer immergé sur les 200 cellules de la frontière est, avec intérieur plus élevé.
- Conservation de masse d'eau, énergie et matière sèche : anomalies non observées au pas 0 sur chacun des 6 profils ; <1e-14 à 150 pas sous profil Montagnes seed 123.
- Reproductibilité après 150 pas : régénération avec le même (profil, seed) => **égalité exacte** des tableaux terrain, eau de surface, nappe.
- Accordéon fermé initialement, ouverture et bouton de génération testés.
- Chromium sous Xvfb avec WebGL2 SwiftShader : 2 générations sans erreur de shader.
- Tests physiques de longue durée (2 000 pas) existants sur couche 16 ; non répétés sur tous les presets. Rendu GPU matériel Windows à vérifier.

## Sources
- [HTML autonome Couche 17](Monde_VJ_Atlas_3D_Couche_17_Interface_Simplifiee.html)
- [README](README.md)

## Gouvernance
Branche expérimentale `prototype/couche-17-interface-simplifiee`, issue de `prototype/couche-16-nappes-phreatiques`. La branche `main` n'est pas modifiée. Aucun changement volontaire aux lois de simulation : cette couche modifie l'interface et les valeurs paramétriques utilisées à la génération.
