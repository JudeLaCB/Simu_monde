# Simu_monde

Simu_monde est un laboratoire de simulation d'un monde 3D évolutif : des ressources circulent entre l'environnement, les végétaux et les animaux, puis les modèles gagnent progressivement en réalisme, en physique et en complexité.

## Principe central

La simulation du monde est indépendante de son rendu.

```text
                SIMULATION CORE
        état + règles + temps + hasard seedé
                     |
          +----------+----------+
          |                     |
      Headless runner        3D adapter
   tests / métriques /       rendu / caméra /
   accélération temporelle   interaction
```

Le coeur doit pouvoir simuler le monde sans fenêtre graphique. La 3D observe et représente l'état du monde ; elle ne devient pas la source de vérité des règles écologiques.

## Philosophie

1. commencer par le plus petit cycle cohérent ;
2. expliciter les unités, sources, puits et transformations ;
3. rendre le résultat déterministe pour une seed donnée ;
4. tester les invariants avant d'ajouter du réalisme ;
5. ajouter un seul niveau de complexité à la fois ;
6. mesurer avant d'optimiser ;
7. garder les modèles remplaçables.

Exemple de progression :

```text
eau
 ↓
sol → plante → animal
 ↑       ↓        ↓
 └── décomposition / rejets
        ↓
    atmosphère
        ↓
       pluie
```

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

## État

**Phase 0 — fondations.**

Le premier objectif n'est pas encore de construire un monde riche, mais de mettre en place un noyau de simulation testable, déterministe et extensible.

La première milestone fonctionnelle sera un **vertical slice écologique minimal** exécuté en headless, puis visualisé en 3D avec des formes simples.

## Documentation

- [Instructions agents](AGENTS.md)
- [Index documentation](docs/README.md)
- [Architecture](docs/architecture.md)
- [Principes de simulation](docs/simulation_principles.md)
- [Roadmap](docs/roadmap.md)
- [Workflow de développement](docs/development_workflow.md)
- [État courant / handoff](docs/project_handoff_report.md)
