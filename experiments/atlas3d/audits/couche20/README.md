# Audit physique de la couche 20

Consulter le [rapport d'audit](AUDIT_PHYSIQUE.md). Le code du simulateur est identique à celui de la branche `prototype/couche-20-atmosphere-stratifiee` : **aucune correction n'a été appliquée pendant cette phase**.

## État
- Tests indépendants courts sur sept climats (100 pas chacun).
- Stress supplémentaires à 500 pas en froid et sécheresse.
- Tests ciblés : infiltration théorique, source sans gradient, transfert périodique de vapeur, détection `NaN` manquante.
- Les comparaisons 2 000 pas proviennent du développement antérieur sauf indication contraire.

**Décision de gouvernance :** corriger le contrôleur numérique (P0) avant toute autre extension physique. Les priorités P1/P2 et critères de validation figurent dans le rapport.
