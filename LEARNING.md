# Journal d'apprentissage

Une ligne par notion apprise. Les lignes ci-dessous sont des amorces à reformuler. Complète la colonne « Preuve » avec un commit, un test ou un graphique.

| Date | Notion | Ce que j'en retiens | Où dans le projet | Preuve |
|---|---|---|---|---|
| à compléter | Git et SSH | Une clé SSH remplace le mot de passe ; `git add`, `commit`, `push` en trois temps | Dépôt `pension-sustainability-simulator` | Premier commit |
| 23/11/2026 | Données brutes jamais versionnées | `data/raw/` est dans `.gitignore` ; seule une fiche de provenance est commitée | `docs/donnees.md` | `git status` propre |
| à compléter | Régime par répartition | $R_{t+1} = R_t(1+r_t) - D_t$ avec $D_t = B_t - C_t - F_t$ | Cahier des charges, 4.2 | |
| à compléter | Taux d'emploi conditionnel | $e = e^{\text{obs}}/(1-\rho)$, pour ne pas compter deux fois les retraités | Cahier des charges, 3.5 | |
| 25/11/2026 | Calibration et condition d'équilibre | $\tau_0 = B_{2026}/A_{2026}$ équilibre 2026 par construction, ce n'est pas un résultat | Cahier des charges, 6.2 | |
| 25/11/2026 | Valeurs sourcées et statuts | Observé, projection officielle, calibré, hypothèse documentée, convention | `docs/hypotheses.md` | |
| 25/11/2026 | NumPy : `shape` et `axis` | `sum(axis=k)` fait disparaître l'axe k : sur `N[s, a]`, `axis=0` donne la population par âge, `axis=1` par sexe | `src/demography/population.py` (`by_age`) | `tests/test_demography.py` |
| 25/11/2026 | NumPy : broadcasting | Un vecteur de survie `(S, A+1)` multiplie tout `N[c, s, a]` sans boucle : `n * surv[None, :, a0:]` | `src/demography/engine.py` | `tests/test_toy_example.py` |
| 25/11/2026 | pandas : lire un onglet Excel mal formaté | `header=None` pour voir le brut, puis `skiprows`, `nrows`, `usecols`, `names` ; on vérifie la somme contre le total publié | `src/data_io/insee.py` | `tests/test_insee_io.py` |
| 25/11/2026 | Âge révolu et âge atteint | L'âge révolu a au 1er janvier devient a+1 dans l'année ; avec un décalage d'un an, l'écart sur 2027 serait de 64 % au lieu de 0,1 % | `docs/conventions-moteur.md` | `docs/comparabilite-insee.md`, vérification 3 |
| 25/11/2026 | Cas jouet calculé à la main | Référence de vérité indépendante du code : le test échoue au moindre chiffre faux à 1e-9 | `tests/test_toy_example.py` | `pytest` vert |
| 25/11/2026 | `pytest`, `pytest.approx`, tests ignorés | Comparaison de flottants avec tolérance ; les tests qui lisent `data/raw/` sont ignorés s'il est absent | `tests/` | 42 tests en local |
| 25/11/2026 | Pas de correction silencieuse | Départs migratoires supérieurs à l'effectif : exception (`raise`) ou alerte (`log_only`), jamais de troncature | `src/demography/migration.py` | Test T10 |
| 25/11/2026 | GitHub Actions | Un workflow = `on`, `jobs`, `steps` : installer les dépendances puis lancer `pytest` à chaque push | `.github/workflows/tests.yml` | Onglet Actions du dépôt |
| 25/11/2026 | Piège : `>` en PowerShell | Dans Windows PowerShell 5, `>` écrit en UTF-16 et Git voit un fichier binaire ; utiliser `Set-Content -Encoding ascii` | `requirements-lock.txt` | Commit du lock |
| 25/11/2026 | Piège : un paquet `io` masque le module standard | Nommer le paquet `data_io` | `src/data_io/` | `docs/architecture.md`, section 8 |

## À apprendre ensuite (phase 2)

Coche une case quand tu sais refaire la notion seul, sans le code sous les yeux.

- [ ] NumPy : tableaux, `broadcasting`, `axis`
- [ ] pandas : lecture de fichiers Excel, filtres
- [ ] `pytest` et `pytest.approx`
- [ ] matplotlib : pyramide des âges
- [ ] GitHub Actions : un workflow minimal qui lance les tests


