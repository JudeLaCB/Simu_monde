# Couche 20.1 — Rapport de développement

Statut : **prototype correctif validé sur tests ciblés, test long incomplet**. Base : `prototype/couche-20-atmosphere-stratifiee` et constat de `audit/couche-20-physique`. Aucun merge automatique.

## Réalisé

- [x] Détection finie (`Number.isFinite`) et vérifications de bornes sur tous les principaux stocks, capacité et géologie, au début et à la fin d'un pas ; diagnostic cellule/réservoir.
- [x] Plafond d'infiltration dépendant des caractéristiques procédurales du sol et de sa saturation (2–32 mm/h au maximum avant ajustement par saturation).
- [x] Échanges nappe/lac/rivière avec les aquifères voisins régis par un gradient de charge, avec aucune résurgence au gradient nul.
- [x] Transport atmosphérique bilinéaire conservatif à frontières fermées pour modèle ancien et modèle à six couches.
- [x] Interface simple et modèles physiques existants préservés ; faune toujours en pause.
- [x] Tests automatisés du signe des flux, du transport aux frontières et des injections d'anomalies.
- [x] Test rendu WebGL2 SwiftShader/Xvfb sans erreur.
- [ ] 2 000 pas continus confirmés avec banc indépendant et vrai GPU Windows.
- [ ] Thermodynamique locale à six niveaux, saturation thermodynamique et humidité/vent couplés.
- [ ] Registre indépendant des flux énergétiques et transfert local de l'enthalpie.

## Valeurs obtenues

| Test | Résultat |
|---|---|
| Infiltration, seed 42 sur le premier monde | 4,35–22,29 mm/h de capacité nominale suivant cellules (plage légale 2–32) |
| Gradient rivière–nappe nul | 0 m transféré |
| Banque plus haute que rivière | Gain positif, volume équilibré |
| Rivière plus haute que nappes | Perte positive, volume équilibré |
| Vapeur déplacée au bord Est | 100 kg conservés, 0 kg au bord Ouest |
| NaN dans nappe cellule 20200 | Arrêt au pas 0, diagnostic `nappe[20200]` |
| Infini vapeur, eau négative, nappe dépassée, chaleur/roche NaN | Alerte immédiate à chaque injection |
| Tempéré 120 pas | Erreur relative eau 2,20e-15, énergie 3,99e-16 |
| Aride 80 pas | Erreur eau 1,50e-14, énergie 2,66e-16 |
| Tropical 80 pas | Erreur eau 5,14e-15, énergie 2,66e-16 |
| Polaire 125 pas | Erreur eau 5,69e-15, énergie 7,99e-16 |
| Sécheresse 125 pas | Erreur eau 5,45e-15, énergie 5,31e-16 |
| Tempéré long | 1 200 pas segmentés atteints, sans écart >1e-9 ; épreuve suivante interrompue |

## Portée de la validation

L'intégrité des **bilans élargis** reste vérifiée, mais ne valide pas encore l'exactitude des flux thermiques et hydrologiques locaux. Le ralentissement du navigateur de test sur les trajectoires longues n'est pas attribué formellement au nouveau contrôle ; un profilage Windows est nécessaire avant d'en déduire sa cause.

Voir [README.md](README.md) et les scripts/JSON de vérification livrés avec l'archive.