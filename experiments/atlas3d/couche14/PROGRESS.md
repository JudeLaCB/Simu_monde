# Monde VJ — Couche 14 : réseau hydrographique (étape A)

**Statut : prototype en test.** Branche expérimentale issue de `prototype/couche-13-meteo-dynamique`. L'ancien cœur 2D de `main` reste intact.

## Décision produit

- Mettre en place un **réseau hydrographique morphologique** avant de modifier les équations d'écoulement.
- Conserver 2 × 2 km, résolution 10 m, **2 000 pas/jour**, météo et nuages de la couche 13.
- **Mettre temporairement en pause tous les herbivores/carnivores** pour réduire le coût numérique. Les codes et paramètres animaux sont conservés, mais aucune initialisation, chasse, reproduction ou consommation n'est exécutée.
- Conserver l'eau totale, la matière sèche et l'énergie ; aucun débit de source artificielle.

## Avancement

- [x] Génération de chemins de drainage D4 en pente descendante (voisinage identique au moteur d'échange d'eau).
- [x] Accumulation des apports amont (proxy topographique, **pas** un débit hydrologique en m³/s).
- [x] Chenaux creusés avant la création des stocks d'eau et avant leur bilan énergétique.
- [x] Largeur/teinte visuelles des lits, diagnostic bassin / longueur / portions en eau ; mini-carte dédiée.
- [x] Paramètres réglables : seuil de formation, profondeur de creusement, activation du réseau pour comparaison A/B.
- [x] Faune désactivée dans la boucle physique, commandes et télémétrie mises en retrait.
- [x] Premier test Chromium : 100 pas, aucune erreur JavaScript, bilans massique/énergétique stables.
- [x] 2 000 pas validés avec erreur relative eau/énergie/matière sèche < 1e-14.
- [x] Suspension vérifiée aux seuils 4 000 / 6 000 par saut ciblé de l'horloge dans le banc d'essai (pas une simulation continue jusqu'à ces pas).
- [ ] Valider le rendu GPU WebGL2 sous Windows ; Chromium CI utilise Canvas de secours.
- [x] HTML autonome et ZIP Windows créés ; le réseau est bien un *lit* topographique, sans ajout d'eau.

## Exemples de mesures (seed 42, 120 cellules en amont)

- 40 000 cellules et 4 km².
- 1 253 cellules de chenal, environ 12,02 km de segments reliés, 51 microbassins associés à un lit.
- Profondeur maximale de creusement : 4,31 m (relief normalisé à z=0 ensuite).
- Aucun tronçon de chenal remontant vers son aval sur cette seed après incision (vérifié automatiquement).
- Au pas 100, l'eau est physiquement présente dans 717 cellules de chenal (pas de source d'eau imposée).

## Limites connues

Le réseau est actuellement produit par drainage strictement descendant avec minima locaux (bassins fermés). Une partie des ruisseaux reste sèche selon la pluie et la perméabilité. Les chemins ne sont pas encore un solveur 1D des débits, et l'érosion n'évolue pas au fil du temps. Le contrôle visuel montre les lits secs en terre et uniquement les cellules mouillées en bleu. Les classes géomorphologiques et le calcul de conservation restent ceux de la couche 13.

L'étape B (mesure de débit, adaptation des pertes, éventuel recalibrage hydraulique) ne doit commencer qu'après validation de cette étape A.

## Bilan de validation de l'étape A

- Source complète : [HTML couche 14](Monde_VJ_Atlas_3D_Couche_14_Reseau_Hydrographique.html).
- **2 000 pas continus testés** (seed 42) : erreurs relatives masse, énergie et matière sèche toutes < 1e-14, 3 554 cellules végétalisées au pas 2 000.
- **1 253 cellules de chenal / 12,02 km**, 51 petits sous-bassins avec chenaux ; aucune remontée topographique vers l'aval parmi les arcs retenus.
- Rivières activées / désactivées à seed identique : géométrie de terrain effectivement différente, quantité totale d'eau identique.
- Même seed après régénération = même masque de chenaux ; seuil réglable validé et affichage des lits décochable.
- Faune suspendue : zéro herbivore et zéro carnivore dans la simulation 2 000 pas ; garde logique testée lors du passage des seuils 4 000 et 6 000 par **sauts instrumentés** dans une copie du HTML.
- Rendu Chromium Canvas : zéro exception JavaScript ; WebGL2 GPU toujours à vérifier sur Windows.
- Test continu plus long interrompu par le banc de test Chromium (limite de ressources / temps), sans constat d'un échec d'invariant jusqu'à 2 000 pas.
- Aucun merge vers la branche `main`. Étape B non engagée.
