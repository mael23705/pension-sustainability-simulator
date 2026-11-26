# Bilan de la phase 3 : moteur financier et calibration de 2026 (26 novembre 2026)

Projet : `pension-sustainability-simulator`. Statut : **phase 3 terminée**, sous réserve de la validation des conventions D20 à D24 (section 5) ; phase 4 (indicateurs actuariels) à démarrer.

## 1. Résumé

Le moteur calcule, pour chaque année de 2026 à 2065, les cotisants, les retraités, l'assiette, les prestations, les cotisations, le déficit $D_t = B_t - C_t - F_t$ et la réserve $R_t$ (jusqu'en 2066). Il est calibré sur 2026 : $\tau_0 = B_{2026}/A_{2026}$ rend $D_{2026}$ nul **par construction** (ce n'est pas un résultat). Il est entièrement vectorisé : un axe `sim` en tête des trajectoires macroéconomiques, une seule boucle Python, sur les années, pour la réserve. Le cas jouet financier, calculé à la main, est reproduit à $10^{-9}$ près.

## 2. Résultats publiés (scénario central, $k = 0$, `scripts/plot_finance.py`)

Ces chiffres sont **conditionnels aux hypothèses** (D6 à D24) ; ils décrivent le modèle, pas le système français.

| Grandeur | Valeur |
|---|---|
| Taux de calibration $\tau_0$ | 27,81 % (taux du modèle, pas un taux légal) |
| Coefficient de recalage du stock $\lambda$ | 1,0850 (dépense du moteur avant recalage 325,6 Md€, référence 353,2 Md€, écart −7,84 %) |
| Retraités en 2026 | 16,43 millions dans le moteur ; 17,30 millions dans l'EACR |
| Cotisants / retraités | 29,74 M / 16,43 M en 2026 ; 27,61 M / 20,90 M en 2065 |
| Prestations 2026 → 2065 | 353,2 → 549,3 Md€ (euros constants 2026) |
| Déficit 2027 → 2065 | 5,0 → 111,1 Md€ |
| Réserve de fin d'année 2065 | −2 023 Md€ (réserve initiale nulle) |
| Perte d'emploi D16 en 2026 | 2,72 % de l'emploi couvert ($\delta$ central) ; 2,08 % à $\delta + 1$, 3,55 % à $\delta - 1$ |

Graphique : `docs/figures/finance-2026-2065.png` (six panneaux). Calibration complète : `scripts/calibrate_phase3.py` ($\delta_{c,s}$, facteur d'échelle de l'emploi 1,0414, $\kappa_{c,s}$, $\lambda$, $\theta_{c,s}$).

## 3. Livrables

| Fichier | Rôle |
|---|---|
| `src/data_io/eacr.py` | Lecture des tables EACR (stock, nouveaux liquidants, âges) ; lignes à $m_1$ manquant écartées et comptées |
| `src/economics/employment.py` | Profil d'emploi, facteur d'échelle (D6), taux conditionnel $e = e^{obs}/(1-\bar\rho)$ sans troncature (D16), $\varphi$ (D18b) |
| `src/economics/macro.py` | Transitions linéaires 2026→2040, indice de salaire $G$, scénarios favorable/central/défavorable (D18) |
| `src/economics/wages.py` | Salaires annuels bruts par catégorie, sexe et âge (D22) |
| `src/actuarial_model/retirement.py` | Âge de départ $a^*_{c,s}(g)$, grille de retraités, $\bar\rho$ |
| `src/actuarial_model/calibration.py` | $\delta$, $\kappa$, $\lambda$, $\theta$, $\tau_0$ (formes fermées) |
| `src/actuarial_model/finance.py`, `model.py` | Cotisations, déficit, réserves ; construction des entrées et exécution `run_finance` |
| `scripts/calibrate_phase3.py`, `plot_finance.py`, `build_*_table.py` | Publication de la calibration, figure, tables dérivées (ignorées par Git) |
| `notebooks/02_vectorisation.ipynb` | Exercices de vectorisation avec solutions |
| `tests/` | 115 tests (dont T8, T11, cas jouet financier, contrôles indépendants) |
| `docs/hypotheses.md`, `docs/donnees.md` | Décisions D20 à D24 ; tables dérivées, DREES 3/4, salaires, inflation |

## 4. Constats

- **Le stock de retraités du moteur est inférieur à l'EACR** (16,43 M contre 17,30 M) ; l'écart vient des hommes (7,24 M contre 8,11 M). Il vient de la règle de départ en escalier ($\rho$ vaut 0 ou 1) et de $\delta$ ; il n'est pas corrigé (voir `docs/hypotheses.md`, section 6, point 11). Le coefficient $\lambda$ compense en montant, pas en effectifs.
- **$\lambda$ = 1,085 n'est pas un paramètre de comportement** : c'est un résidu de calibration qui absorbe les différences de champ (régimes, réversion, minima) entre l'EACR et DREES. Il est publié et ne doit pas être interprété économiquement.
- **L'arrondi entier de l'âge légal (D5) crée un coude vers 2030-2031** : la génération 1967 part à 64 ans d'un seul coup. C'est un effet de la convention, pas de la démographie.
- Le niveau commun des salaires n'a **aucun effet** sur $D_t$ et $R_t$ (D22) : seule compte l'évolution relative ; d'où l'absence de sensibilité au niveau de salaire.
- Aucune erreur $e > 1$ dans les neuf scénarios testés ($\delta \pm 1$ × trois trajectoires macro) ; la perte d'emploi D16 reste entre 1,9 % et 3,6 % de l'emploi couvert.

## 5. Points ouverts

1. Valider D20 (λ appliqué au stock et aux nouveaux liquidants ; $\bar w$ comme proxy de la carrière) et D21 (partage stock/nouveaux par génération ; classe ouverte rattachée à la génération $t - A$, limitation d'environ 0,6 % de $B$ en 2065).
2. Confirmer D23 (lignes EACR sans $m_1$ écartées) et la valeur $g_{2026} = 0,7\ \%$ (convention D18).
3. Décider si l'âge de départ est lissé (distribution des âges de liquidation) en phase 4 pour supprimer le coude de 2030-2031.
4. Fixer pour la phase 5 les lois des trajectoires $G$, $\varphi$, $r$ : la phase 3 ne fournit que des scénarios déterministes.

## 6. Limites et vigilances

- Un seul régime consolidé ; affiliations fixes ; pas de réversion, de minima, de décote ni de surcote.
- Population déterministe : les simulations de la phase 5 ne feront varier que $G$, $\varphi$ et $r$.
- Les flux utilisent la population au 1er janvier (D24) ; toutes les simulations doivent partager les valeurs de 2026, sinon `ConfigError`.
- La classe ouverte (100 ans et plus) mélange plusieurs générations ; effet mesuré, faible.
- Le modèle reste conditionnel à ses hypothèses : aucune recommandation politique.

## 7. Leçons de la phase

- **Les mutations ont une fois encore révélé des tests manquants** : retirer le facteur $(1-\rho)$ des cotisants, mal indexer la matrice des nouveaux liquidants ou inverser les sexes de $\delta$ passait tous les premiers tests. Des vérifications indépendantes à boucles explicites (`tests/test_independent_checks.py`) tuent désormais les douze mutations essayées.
- Un test avec des données aléatoires peut violer lui-même la règle $e \le 1$ : fabriquer les données de test à partir de la contrainte, pas l'inverse.
- Une valeur par défaut cachée (`calibration_year`) est une correction silencieuse : tout passe par `get_param`.
- Les lignes à secret statistique (NaN) doivent être écartées *et comptées*, sinon les calibrations deviennent NaN sans message.
- Vectoriser sur les simulations et boucler seulement sur les années : la réserve est récurrente, le reste ne l'est pas.
