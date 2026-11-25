# Bilan de la phase 2 : moteur démographique (25 novembre 2026)

Projet : `pension-sustainability-simulator`. Statut : **phase 2 terminée**, sous réserve de la validation des conventions listées en section 5 ; phase 3 (moteur financier) à démarrer.

## 1. Résumé

Le moteur projette la population par catégorie d'affiliation, sexe et âge de 2026 à 2066, dans l'ordre mortalité → vieillissement → migrations → naissances, avec une classe ouverte à 100 ans et plus. Alimenté avec les hypothèses de la projection Insee 2026 (scénario central), il retrouve ses populations très en deçà des seuils fixés avant les tests. Le cas jouet, calculé à la main, est reproduit à 10⁻⁹ près.

## 2. Résultats (`scripts/run_insee_reproduction.py`)

| Grandeur | Seuil | Écart maximal sur 2026-2066 |
|---|---|---|
| Population totale | 1 % | 0,139 % |
| 0-19 ans | 2 % | 0,474 % |
| 20-59 ans | 2 % | 0,139 % |
| 60 ans et plus | 2 % | 0,010 % |

Aucune alerte de migration, aucun effectif négatif. Graphique : `docs/figures/ecarts-insee.png`. Cette comparaison contrôle l'implémentation ; elle ne valide pas la capacité à prévoir la démographie (plan de validation, section 1).

## 3. Livrables

| Fichier | Rôle |
|---|---|
| `src/config.py`, `src/conventions.py` | Lecture du YAML sans valeur par défaut silencieuse ; indices des sexes, unités |
| `src/data_io/insee.py` | Lecture de POP3 et de la projection Insee, agrégation de la classe ouverte, paramètres annuels |
| `src/demography/` | Structures, catégories, migrations en flux bruts, transition annuelle, comparaison |
| `src/actuarial_model/retirement.py` | Part de retraités ρ (test T8) |
| `tests/` | 42 tests : T1 à T10, T12, cas jouet, lecture Insee, reproduction Insee |
| `scripts/` | Fichiers bruts, six vérifications de comparabilité, reproduction, graphiques |
| `.github/workflows/tests.yml` | `pytest` à chaque push |
| `docs/conventions-moteur.md`, `docs/comparabilite-insee.md` | Choix de modélisation ; résultats des vérifications du 25/11/2026 |

## 4. Constats sur les données

- La population « France » de POP3 est **identique** à celle de la projection, et d'après les notes des fichiers elle **inclut Mayotte** à partir de 2014 (le plan supposait « hors Mayotte »).
- La projection contient un **« ajustement »** (63 000 en 2026, 16 000 en 2027, nul ensuite) en plus du solde migratoire ; sans lui, l'écart de 2027 est de −0,09 % au lieu de −0,003 %.
- Naissances 2026 : −0,40 % par rapport à l'Insee avec les femmes présentes au 1er janvier (cahier 3.7), +0,000 % avec la moyenne des effectifs de début et de fin d'année. Cet écart de convention explique l'essentiel de l'écart sur les 0-19 ans.
- Les tests qui lisent `data/raw/` sont ignorés dans GitHub Actions (fichiers non versionnés) : seuls les tests mécaniques y tournent.

## 5. Points ouverts

1. Valider la convention du solde migratoire de l'âge 0 (appliqué aux nouveau-nés, après les naissances) et celle du quotient de la classe ouverte (`docs/conventions-moteur.md`, section 2).
2. Confirmer la nature de l'« ajustement » de l'Insee dans sa documentation.
3. Choisir pour la phase 3 la base de calcul des naissances (cahier : femmes présentes au 1er janvier ; l'Insee semble utiliser la moyenne début/fin d'année).
4. Test T11 (taux d'emploi) : phase 3.
5. Les neuf points ouverts du bilan de la phase 1 restent reportés en phase 3.

## 6. Limites et vigilances

- Une seule table de mortalité pour toutes les catégories ; parts π_c identiques par âge et par sexe.
- La pondération du quotient de la classe ouverte utilise la population Insee de l'année : elle devra venir du modèle lui-même quand il ne sera plus calé sur l'Insee.
- Le modèle reste conditionnel à ses hypothèses : aucune recommandation politique.

## 7. Leçons de la phase

- `pip freeze > fichier` sous Windows PowerShell 5 écrit en UTF-16 : Git voit un fichier binaire. Utiliser `Set-Content -Encoding ascii`.
- Un paquet nommé `io` masque le module standard : `src/io/` a été remplacé par `src/data_io/`.
- Deux lignes pour le même paquet dans `requirements.txt` font échouer `pip install` (« Double requirement given »).
- `data/processed/` doit être ignoré par Git comme `data/raw/`.
- Un test qui passe du premier coup mérite un doute : des bugs introduits volontairement (mutations) ont montré qu'un test manquait (inversion filles/garçons).

## 8. Suite

Phase 3 : moteur financier (taux d'emploi conditionnel, salaires, retraite, cotisations, déficit, réserves) et calibration de 2026 ($\tau_0 = B_{2026}/A_{2026}$, $D_{2026} = 0$). Voir le cahier des charges, section 8.
