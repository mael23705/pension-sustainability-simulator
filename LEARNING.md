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

## À apprendre ensuite (phase 2)

- [ ] NumPy : tableaux, `broadcasting`, `axis`
- [ ] pandas : lecture de fichiers Excel, filtres
- [ ] `pytest` et `pytest.approx`
- [ ] matplotlib : pyramide des âges
- [ ] GitHub Actions : un workflow minimal qui lance les tests

Chaque notion : 1 à 3 heures, puis une ligne ici.
