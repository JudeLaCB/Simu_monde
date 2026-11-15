# Monde VJ — Couche 20.2, rapport de réalisation

Statut : **prototype correctif testé sur scénarios ciblés ; test long restant**. Branche issue de `fix/couche-20-1-fiabilisation-physique`.

## Travaux
- [x] Conditions périodiques de transport en 6 couches et sur le moteur atmosphérique de secours.
- [x] Smoothing visuel périodique, nuages visibles des deux côtés de la couture.
- [x] Regroupement visuel en 3 bandes d'altitudes et interpolation graphique entre les transports physiques (toujours toutes les 8 itérations).
- [x] Conservation de la masse vérifiée, vent préservé.
- [x] Régression chiffrée contre 20.1, WebGL2 et Canvas testés.
- [x] Bilans sur 350 pas tempérés et 130 pas polaires.
- [ ] Test continu de 2 000 pas avec GPU Windows matériel.
- [ ] Champs atmosphériques thermodynamiques indépendants par niveau (prochaine étape).

## Comparaison identique (Montagnes, Tropical humide, seed 42)
| Pas | Version | Masse nuageuse totale kg | Maximum par cellule kg | Part en bordure (6 cellules) |
|---:|---|---:|---:|---:|
| 16 | 20.1 | 1 165 371 | 6 471 | 19,15 % |
| 16 | 20.2 | 1 133 177 | 237 | 12,79 % |
| 32 | 20.1 | 685 347 | 14 404 | 28,94 % |
| 32 | 20.2 | 641 450 | 153 | 13,77 % |
| 64 | 20.1 | 338 920 | 22 593 | 49,00 % |
| 64 | 20.2 | 289 768 | 123 | 17,59 % |

La **différence des totaux de nuages** entre deux modèles est normale : la redistribution influence les zones de saturation et de précipitation, bien que la quantité *totale d'eau du monde* reste conservée.

## Tests dirigés
- 100 kg vapeur + 50 kg nuages injectés à x=199 (bande k=2), vent Est : 100 kg vapeur et 50 kg nuages conservés, ~99,996 kg de vapeur atteignent la bande ouest (25 colonnes).
- Vent Ouest depuis x=0 : conservation identique, ~99,996 kg atteignent la bande est.
- Version non stratifiée : 100 kg vapeur déplacés depuis l'est vers l'ouest, conservation exacte.
- Montagnes + tropical : 64 pas, erreurs eau 1,506×10⁻¹⁵, énergie 2,656×10⁻¹⁶, matière sèche 0.
- Mixte + tempéré : 350 pas, erreurs eau 8,070×10⁻¹⁵, énergie 2,658×10⁻¹⁶.
- Montagnes + polaire : 130 pas, erreurs eau 1,119×10⁻¹⁴, énergie 9,316×10⁻¹⁶.
- WebGL2 / SwiftShader : rendu actif, nuages en 3 bandes, pluie 3D avec depth test, aucune erreur JS.
- Tentative tropicale prolongée interrompue par une limite navigateur ; **non validée**.

## Précautions
La périodicité ne concerne que vapeur et nuages : géosphère, hydrosphère et cryosphère ont leurs frontières conservées. Les vents peuvent être discontinus de part et d'autre du domaine ; ce choix privilégie un modèle simplifié de monde répété, non un domaine externe réellement ouvert. L'énergie est toujours une comptabilité globale étendue (cf. audit couche 20). Pas de merge automatique.