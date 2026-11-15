# Monde VJ — Couche 20.2 : atmosphère périodique

## Lancement sur Windows
Double-cliquer sur **Lancer_Monde_VJ_20_2.bat**. Sinon ouvrir le fichier HTML directement dans Chrome ou Edge. Le prototype est autonome et fonctionne hors ligne.

## Nouveautés
- **Frontières atmosphériques périodiques :** une masse de vapeur/nuages qui quitte la carte à l'Est réapparaît à l'Ouest ; même principe Nord-Sud.
- **Transport conservatif** : dépôt bilinéaire des six niveaux sur grille périodique, poids positifs dont la somme vaut un ; modèle atmosphérique historique à une couche mis en cohérence.
- **Nuages moins saccadés :** un décalage visuel progressif est calculé entre les mises à jour physiques du transport, toujours effectuées tous les 8 pas. La prévision d'affichage ne modifie jamais les réservoirs physiques.
- **Rendu nuageux en trois bandes :** elles regroupent respectivement les six niveaux atmosphériques 0–200 m, 200–1 000 m et 1 000–4 000 m. Les hauteurs graphiques sont *compressées* pour la lisibilité ; la simulation ne résout pas encore la thermodynamique à chaque niveau.
- **Bords visuels continus** : le lissage des nuages est périodique et les masses sont répliquées uniquement dans le rendu aux coutures pour éviter une coupure brutale.
- **Restent inchangés :** relief géomorphologique, rivières, nappes, cryosphère, météo, infiltrations/sûreté 20.1, 7 paysages, 7 climats, Random Seed, 2 000 pas/jour et faune désactivée.

## Tests
Les tests de transport isolé déplacent 100 kg de vapeur + 50 kg de nuages d'un bord vers l'autre et conservent 150 kg à l'arrondi machine, dans les deux sens. Le vieux transport non stratifié garde aussi 100 kg et les réinjecte de l'autre côté.

Sur *Montagnes + Tropical humide + seed 42*, au pas 32 : maximum des nuages 14 404 kg/cellule pour la 20.1 contre 153 kg/cellule pour la 20.2 ; part des nuages dans une bande de 6 cellules autour de la carte 28,9 % contre 13,8 %. Le champ de vent et sa déviation restent identiques. Au pas 64 : erreur d'eau 1,51×10⁻¹⁵, énergie 2,66×10⁻¹⁶.

Autres essais terminés : tempéré 350 pas (eau 8,07×10⁻¹⁵), polaire 130 pas (eau 1,12×10⁻¹⁴), erreurs d'énergie inférieures à 1×10⁻¹⁵, aucune réactivation des animaux. WebGL2/SW SwiftShader et Canvas démarrent sans exception JS, pluie avec test de profondeur WebGL2 validée.

### Limites et choix scientifiques
- Une **frontière périodique suppose un monde qui se répète** ; elle n'est pas identique à une carte située dans une atmosphère régionale extérieure ouverte.
- Les bords du relief et les vents générés par ce relief ne sont pas eux-mêmes périodiques ; cela peut produire une discontinuité de forçage au passage des frontières.
- Il n'existe pas encore de domaine extérieur imbriqué, d'advection thermodynamique complète ou de nuages réellement volumétriques avec profondeur. Le rendu de nuages reste un Canvas 2D au-dessus de la scène 3D.
- La simulation complète de **2 000 pas n'a pas été validée pour cette correction**. Un essai tropical prolongé dans le banc Chromium a été interrompu sans diagnostic physique concluant.
- Ce prototype ne doit pas être considéré comme une prévision météorologique calibrée.

Tests optionnels : `python test_periodicite.py` avec Playwright Chromium installé (`pip install playwright` puis `playwright install chromium`). Les tests ne modifient pas l'HTML original.

Branche GitHub : `fix/couche-20-2-atmosphere-periodique`, sans fusion dans `main`.