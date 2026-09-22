# Simu_monde

Simu_monde est un laboratoire de simulation d'un monde écologique évolutif. La V1 est volontairement **strictement 2D** : des ressources circulent entre l'environnement, les végétaux et les animaux, puis les modèles gagnent progressivement en réalisme et en complexité.

## Principe central

La simulation du monde est indépendante de son rendu.

```text
                SIMULATION CORE
        état + règles + temps + hasard seedé
                     |
          +----------+----------+
          |                     |
      Headless runner       Visualisation 2D
   tests / métriques /      rendu / caméra /
   accélération temporelle  interaction
```

Le coeur doit pouvoir simuler le monde sans fenêtre graphique. La visualisation 2D observe et représente l'état du monde ; elle ne devient pas la source de vérité des règles écologiques.

## Philosophie

1. commencer par le plus petit cycle cohérent ;
2. expliciter les unités, sources, puits et transformations ;
3. rendre le résultat déterministe pour une seed donnée ;
4. tester les invariants avant d'ajouter du réalisme ;
5. ajouter un seul niveau de complexité à la fois ;
6. mesurer avant d'optimiser ;
7. garder les modèles remplaçables.

## Décision spatiale V1

La première version du monde est **2D**.

Aucune décision n'est encore figée sur :
- grille ou espace continu ;
- taille du monde ;
- frontières ;
- représentation de l'eau ;
- moteur de visualisation.

Ces sujets seront décidés séparément.

## Méthode de travail

```text
Jude
  ↓ objectif / validation du comportement
Primary ChatGPT Pilot
  ↓ contrat + architecture + invariants
Codex
  ↓ code + tests + PR
Primary Pilot
  ↓ review
Jude
  ↓ merge
```

GitHub est la mémoire durable du projet ; le chat sert au raisonnement interactif.

## Quick start

Pré-requis : Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
python -m mypy src tests
```

Sous Linux/WSL :

```bash
source .venv/bin/activate
```

## État

**Phase 0 — fondations.**

La première milestone fonctionnelle sera un **vertical slice écologique minimal 2D**, d'abord exécuté en headless puis visualisé simplement.

## Documentation

- [Instructions agents](AGENTS.md)
- [Index documentation](docs/README.md)
- [Architecture](docs/architecture.md)
- [Principes de simulation](docs/simulation_principles.md)
- [Roadmap](docs/roadmap.md)
- [Workflow de développement](docs/development_workflow.md)
- [État courant / handoff](docs/project_handoff_report.md)
