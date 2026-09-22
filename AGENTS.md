# AGENTS.md — Simu_monde

Ce fichier définit les règles permanentes de travail pour tout agent IA intervenant sur Simu_monde.

## 1. Source de vérité

GitHub est la mémoire durable du projet. Le chat est un contexte de travail, jamais l'autorité finale.

Ordre d'autorité :

1. décision explicite actuelle de Jude ;
2. ce `AGENTS.md` ;
3. contrat/spec approuvé du travail actif ;
4. documents d'architecture et de principes de simulation ;
5. comportement fusionné sur `main` pour l'état réellement implémenté ;
6. avis d'un reviewer ou spécialiste, seulement après synthèse du Primary Pilot.

Le live GitHub détermine l'état des branches, PR, issues et CI. Les docs portent le WHY, les contrats et les décisions durables.

## 2. Rôles

### Jude — Product Owner / World Designer

Jude garde l'autorité finale sur :

- la direction du monde simulé ;
- le niveau de réalisme recherché ;
- les compromis jeu / simulation ;
- les nouvelles règles durables de biologie, physique ou écologie ;
- les priorités ;
- l'acceptation fonctionnelle ;
- les merges.

### Primary ChatGPT Pilot — control plane

Le Primary Pilot est responsable de :

- transformer l'idée en incréments testables ;
- architecture et décomposition ;
- choix des abstractions et interfaces structurantes ;
- définition des modèles, hypothèses, unités et invariants ;
- classification du risque ;
- préparation des tâches Codex ;
- review des PR et preuves ;
- convergence documentaire.

Le Primary doit réduire la tâche à un problème d'exécution borné avant d'envoyer Codex sur tout changement STANDARD non mécanique ou HIGH-RISK.

### Codex — implementation engineer

Codex possède le HOW local dans les limites du contrat approuvé :

- code ;
- tests ;
- diagnostics ;
- refactors bornés ;
- commits et PR ;
- self-review.

Codex ne doit pas inventer silencieusement :

- une nouvelle loi du monde ;
- une nouvelle source ou disparition de matière/énergie ;
- une unité implicite ;
- un ordre d'intégration ayant un impact sémantique ;
- une architecture core/3D différente de celle approuvée ;
- une nouvelle forme de hasard non déterministe ;
- une approximation scientifique structurante.

### Reviewers read-only

Des reviewers peuvent challenger architecture, modèle, tests, numérique ou performances, mais ne deviennent pas une source d'autorité parallèle.

## 3. Principe de concurrence

> Plusieurs lecteurs peuvent travailler en parallèle ; un seul writer possède une branche active.

- `codex/...` : writer Codex ;
- `pilot/...` : writer Primary Pilot ;
- reviewers : read/comment-only ;
- transfert de writer uniquement par handoff explicite ;
- aucun agent ne merge sa propre PR.

## 4. Principe architectural fondamental

> Le moteur de simulation est indépendant du rendu 3D.

Le core doit fonctionner sans fenêtre, moteur graphique ou fréquence d'affichage.

La couche 3D peut lire des snapshots et transmettre des commandes explicites, mais elle ne doit pas devenir la source de vérité pour :

- l'état biologique ;
- l'eau, la biomasse, les nutriments ou l'énergie ;
- le temps du monde ;
- les décisions d'agent ;
- les règles d'évolution.

Les collisions/forces appartenant réellement à la physique pourront être déléguées à un moteur physique derrière une interface explicite lorsqu'un besoin réel sera défini.

## 5. Invariants de simulation

Tout nouveau système doit préciser, lorsque pertinent :

- variables d'état ;
- unités ;
- entrées ;
- sorties ;
- sources et puits ;
- ordre d'exécution ;
- pas de temps ;
- seed / source de hasard ;
- bornes et cas limites ;
- invariants ou bilans attendus ;
- stratégie de validation.

Règles permanentes :

1. une seed identique + mêmes entrées doit reproduire la même trajectoire, sauf exception explicitement documentée ;
2. le temps de simulation ne dépend pas du framerate ;
3. aucune ressource conservée ne doit apparaître ou disparaître sans source/puits déclaré ;
4. les conversions d'unités doivent être explicites ;
5. une approximation simple validée est préférable à un modèle complexe non validé ;
6. toute optimisation doit préserver les invariants observables ;
7. les paramètres de modèle ne doivent pas être cachés dans le rendu ou dans des nombres magiques dispersés.

## 6. Classification du travail

### SMALL

Travail mécanique/local à faible impact : documentation, renommage, tests additionnels, refactor sans changement de modèle.

Flux :

```text
brief → Codex → tests → self-review → PR → Primary review → Jude merge
```

### STANDARD

Nouveau système borné dont le comportement et les hypothèses sont déjà définis : croissance simple d'une plante, besoin de boire, métrique, nouvel adapter.

Le Primary prépare au minimum :

- objectif ;
- état et flux concernés ;
- unités/hypothèses ;
- architecture/touch points ;
- critères d'acceptation ;
- tests/invariants ;
- non-goals ;
- STOP conditions.

### HIGH-RISK

Est HIGH-RISK tout changement qui modifie notamment :

- représentation du temps ou pas d'intégration ;
- conventions d'unités ;
- conservation de ressources ;
- modèle global d'eau, énergie, masse, nutriments ou biomasse ;
- ordre global des systèmes ;
- déterminisme / RNG ;
- format de sauvegarde durable ;
- frontière core ↔ rendu/physique ;
- architecture structurante ;
- reproduction, génétique ou évolution quand elles changent les hypothèses fondamentales ;
- optimisation susceptible de changer les résultats.

Le Primary prépare une spec reviewable avant code. Jude valide toute nouvelle règle durable du monde qui n'est pas déjà impliquée par une décision existante.

## 7. Validation

Pyramide cible :

```text
unit tests
    ↓
invariant / property tests
    ↓
system integration
    ↓
scenario tests
    ↓
performance / timestep sensitivity
    ↓
visual validation 3D
```

Un résultat visuellement plausible ne prouve pas qu'un modèle est correct.

Pour les quantités conservées, préférer des tests de bilan. Pour le hasard, tester avec seeds fixes. Pour les modèles numériques, ajouter des tests de sensibilité au pas de temps quand cela devient pertinent.

## 8. Complexité progressive

Toujours privilégier :

```text
modèle simple
→ validation
→ observation d'une limite
→ raffinement
```

Ne pas ajouter prématurément :

- météo détaillée ;
- génétique ;
- IA d'apprentissage ;
- terrain complexe ;
- mécanique des fluides ;
- milliers d'entités ;
- optimisation multi-thread/GPU ;
- moteur physique sophistiqué.

Une feature n'entre dans la roadmap active que lorsqu'elle améliore le prochain comportement observable recherché.

## 9. Context budget

Contexte initial normal d'un agent :

1. `AGENTS.md` ;
2. `docs/project_handoff_report.md` ;
3. contrat/spec actif ;
4. code et tests concernés.

Lire `docs/architecture.md` et `docs/simulation_principles.md` pour toute décision structurante ou de modèle.

Éviter de charger l'historique entier du repo lorsque le travail est local.

## 10. STOP conditions

STOP et retour au Primary si l'implémentation exige :

- une nouvelle règle scientifique non définie ;
- une nouvelle unité ou convention globale ;
- une création/destruction implicite de ressource ;
- un changement de timestep ou d'ordre des systèmes ;
- une dépendance forte à un moteur 3D/physique non approuvée ;
- une perte de déterminisme ;
- une optimisation modifiant les résultats ;
- un élargissement de scope uniquement pour faire passer les tests.

Préserver le modèle approuvé plutôt que deviner.
