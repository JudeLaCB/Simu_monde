# Rapport de correction 20.3

Branche `fix/couche-20-3-nuages-stables` depuis `fix/couche-20-2-atmosphere-periodique`. Pas de merge dans `main`.

## Symptôme signalé
Le rendu nuageux avait un tremblement depuis l'ajout des strates atmosphériques. Le modèle de transport n'a pas été retiré ; la dégradation visuelle provenait notamment d'un décalage graphique périodiquement remis à zéro (`tickCount % ATM20_STRIDE` avec `ATM20_STRIDE=8`) et de la séparation en trois bandes d'opacités distinctes.

## Correctifs
- [x] Supprimer les reculs graphiques par phase modulo huit.
- [x] Reprendre le rendu en masses fusionnées comme défaut, alimenté par les six couches physiques.
- [x] Lisser le champ visuel seulement (moyenne exponentielle de coefficient 0,16 par pas).
- [x] Réinitialiser la mémoire visuelle après génération, seed ou activation de l'aperçu artistique.
- [x] Conserver la visualisation des trois bandes en option expérimentale.
- [x] Vérifier l'identité physique des couches 20.2 et 20.3 à seed identique.

## Validation
Montagnes / Tropical humide / seed 42, après 32 pas : `cloudKg` total 641449,863 kg dans les deux versions, bilans strictement égaux et zéro exception JS. Franchissement du pas 7 au 8 : différence moyenne d'image RGB 2,7617 → 1,2974. Test sur Chromium en rendu Canvas de secours ; **aucune validation matérielle WebGL2 Windows** et pas de test continu 2 000 pas sur cette variante.

La nouvelle moyenne des nuages peut être un peu plus lente à réagir que l'évolution physique : c'est un compromis graphique qui reste à valider visuellement.
