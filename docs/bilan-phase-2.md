# Bilan de la phase 2 : moteur démographique (BROUILLON, à compléter)

Projet : `pension-sustainability-simulator`. Statut : code et tests écrits ; à compléter après le premier passage de GitHub Actions et la relecture des conventions de `docs/conventions-moteur.md`.

## 1. Résumé

Le moteur projette la population par catégorie, sexe et âge de 2026 à 2066 (calendrier mortalité → vieillissement → migrations → naissances, classe ouverte à 100 ans et plus). Il reproduit la projection Insee 2026 (scénario central) bien en deçà des seuils fixés.

## 2. Résultats (exécution du 25/11/2026, `scripts/run_insee_reproduction.py`)

| Grandeur | Seuil | Écart maximal sur 2026-2066 |
|---|---|---|
| Population totale | 1 % | 0,139 % |
| 0-19 ans | 2 % | 0,474 % |
| 20-59 ans | 2 % | 0,139 % |
| 60 ans et plus | 2 % | 0,010 % |

Aucune alerte de migration, aucun effectif négatif. Graphique : `docs/figures/ecarts-insee.png`.

## 3. Tests

42 tests (`pytest`) : cas jouet calculé à la main (3 catégories puis une seule), T1 à T10 et T12, lecture des fichiers Insee, reproduction de l'Insee. T11 (taux d'emploi) est reporté en phase 3. Les tests qui lisent `data/raw/` sont ignorés dans GitHub Actions.

## 4. Points à retenir

- Population « France » de POP3 = population de la projection, Mayotte incluse depuis 2014 (le plan supposait « hors Mayotte »).
- La projection Insee contient un « ajustement » (63 000 en 2026, 16 000 en 2027) ajouté au solde migratoire ; sans lui l'écart de 2027 est de −0,09 % au lieu de −0,003 %.
- Écart de convention sur les naissances : −0,40 % en 2026 (femmes présentes au 1er janvier, au lieu de la moyenne début/fin d'année).
- L'écart sur les 0-19 ans (le plus élevé) vient de cet écart de naissances, qui s'accumule.

## 5. Points ouverts

1. Valider les conventions de `docs/conventions-moteur.md` (migration de l'âge 0, quotient de la classe ouverte).
2. Confirmer la nature de l'« ajustement » dans la documentation de l'Insee.
3. Corriger « hors Mayotte » dans `docs/donnees.md` et `docs/plan-de-validation.md`.
4. T11 et le taux d'emploi : phase 3.

## 6. Leçons

À compléter par Maël (notions apprises, une ligne par notion dans `LEARNING.md`).
