# Project Handoff — Simu_monde

**Phase :** 0 — fondations  
**État :** bootstrap initial en préparation  
**Source de vérité live :** GitHub

## Vision actuelle

Construire un simulateur 3D d'écosystème par complexité progressive.

Le premier monde visé comprend à terme :

- eau ;
- végétation ;
- animal herbivore ;
- faim/soif/énergie ;
- rejets ;
- évaporation / retour de l'eau ;
- métriques de cycle.

## Décisions déjà prises

1. Le core de simulation doit fonctionner headless.
2. La 3D est un adapter, pas l'autorité sur l'état écologique.
3. Le temps de simulation utilise un fixed timestep.
4. Le hasard doit être seedé et reproductible.
5. Les unités, sources, puits et invariants sont explicites.
6. On commence avec des modèles simples puis on les raffine.
7. Le moteur 3D n'est pas encore choisi.

## Stack Phase 0

- Python >= 3.11 ;
- pytest ;
- Hypothesis pour property/invariant tests ;
- Ruff ;
- mypy ;
- GitHub Actions.

Pas de dépendance 3D dans le bootstrap.

## Prochaine étape recommandée

Préparer puis implémenter **Phase 1A — Clock + resource ledger**.

Scope cible :

- `SimulationConfig` minimal ;
- `SimulationClock` à fixed timestep ;
- `World` minimal ;
- RNG seedé ;
- plusieurs réservoirs d'eau ;
- transferts explicites ;
- métrique `total_water_kg` ;
- invariant de conservation ;
- runner headless court.

Ne pas ajouter encore plantes, animaux ou rendu 3D dans la même PR.

## Point de décision après Phase 1

Une fois le core minimal stable, évaluer le moteur 3D à partir d'un besoin réel d'intégration, plutôt que de verrouiller l'architecture prématurément.
