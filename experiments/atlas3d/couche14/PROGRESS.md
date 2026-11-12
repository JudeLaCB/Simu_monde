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
- [ ] Vérifier les longues simulations au-delà des anciens pas 4 000 / 6 000.
- [ ] Valider le rendu GPU WebGL2 sous Windows ; Chromium CI utilise Canvas de secours.
- [ ] Finaliser le HTML/ZIP et confirmer que la rivière est bien un *lit* topographique, et non un ajout d'eau.

## Exemples de mesures (seed 42, 120 cellules en amont)

- 40 000 cellules et 4 km².
- 1 253 cellules de chenal, environ 12,02 km de segments reliés, 51 microbassins associés à un lit.
- Profondeur maximale de creusement : 4,31 m (relief normalisé à z=0 ensuite).
- Aucun tronçon de chenal remontant vers son aval sur cette seed après incision (vérifié automatiquement).
- Au pas 100, l'eau est physiquement présente dans 717 cellules de chenal (pas de source d'eau imposée).

## Limites connues

Le réseau est actuellement produit par drainage strictement descendant avec minima locaux (bassins fermés). Une partie des ruisseaux reste sèche selon la pluie et la perméabilité. Les chemins ne sont pas encore un solveur 1D des débits, et l'érosion n'évolue pas au fil du temps. Le contrôle visuel montre les lits secs en terre et uniquement les cellules mouillées en bleu. Les classes géomorphologiques et le calcul de conservation restent ceux de la couche 13.

L'étape B (mesure de débit, adaptation des pertes, éventuel recalibrage hydraulique) ne doit commencer qu'après validation de cette étape A.
