"""Étape 10 : reproduction de la projection Insee 2026 (test 2), tableau et graphique des écarts.

Usage :  python scripts/run_insee_reproduction.py
Écrit docs/figures/ecarts-insee.png et data/processed/ecarts-insee.csv (ignoré par Git).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import _bootstrap
from config import affiliation_shares, get_param, load_config, raw_data_path
from data_io.insee import aggregate_open_class, load_central_projection, load_population_2026, year_params
from demography.comparison import age_group_totals, relative_errors, run_projection
from demography.population import initial_population

R = _bootstrap.RACINE
cfg = load_config(R / "config" / "assumptions.yaml")
A = get_param(cfg, "demography.open_class_age")
a0 = get_param(cfg, "demography.entry_age_a0")
pi = affiliation_shares(cfg)
first = get_param(cfg, "horizon.start_year")
n_steps = get_param(cfg, "horizon.flow_years")
groups = get_param(cfg, "tests.insee_age_groups")
lim_t = get_param(cfg, "tests.insee_total_population_max_relative_error")
lim_g = get_param(cfg, "tests.insee_age_group_max_relative_error")
adj = get_param(cfg, "demography.insee_adjustment_included")

n_init = load_population_2026(raw_data_path(cfg, R, "insee_population_file"),
                              get_param(cfg, "data_files.insee_population_sheet"),
                              get_param(cfg, "data_files.insee_population_scope"))
proj = load_central_projection(raw_data_path(cfg, R, "insee_projection_file"))
state0 = initial_population(aggregate_open_class(n_init, A), a0, pi)
states, results = run_projection(state0, lambda t, _s: year_params(proj, t, A, include_adjustment=adj),
                                 first, n_steps, pi, pi, get_param(cfg, "demography.migration_overflow_policy"))

labels = ["0-19 ans", "20-59 ans", "60 ans et plus"]
rows = []
for k, st in enumerate(states):
    ref = proj.population[:, :, proj.year_index(first + k)].sum(axis=0)
    e_g = relative_errors(age_group_totals(st.by_age().sum(axis=0), groups), age_group_totals(ref, groups))
    rows.append([first + k, relative_errors(st.total(), ref.sum()), *e_g])
df = pd.DataFrame(rows, columns=["annee", "total", *labels]).set_index("annee")
out_csv = R / "data" / "processed"
out_csv.mkdir(parents=True, exist_ok=True)
df.to_csv(out_csv / "ecarts-insee.csv", float_format="%.6f")

print((df * 100).round(3).iloc[::5].to_string())
worst_t, worst_g = df["total"].abs().max(), df[labels].abs().max()
print(f"\nÉcart maximal, population totale : {worst_t:.3%} (seuil {lim_t:.0%}) -> {'OK' if worst_t <= lim_t else 'DÉPASSÉ'}")
for lab in labels:
    print(f"Écart maximal, {lab:<15}: {worst_g[lab]:.3%} (seuil {lim_g:.0%}) -> {'OK' if worst_g[lab] <= lim_g else 'DÉPASSÉ'}")

# --- graphique : un seul axe (écart relatif en %), seuils en pointillés ---
couleurs = {"total": "#257de0", "0-19 ans": "#f47230", "20-59 ans": "#00b894", "60 ans et plus": "#f2a600"}
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
for col, c in couleurs.items():
    ax.plot(df.index, df[col] * 100, color=c, linewidth=2, label="Population totale" if col == "total" else col)
    dy = {"total": -2, "0-19 ans": -4, "20-59 ans": -10, "60 ans et plus": 9}[col]   # évite les chevauchements
    ax.annotate("Total" if col == "total" else col, (df.index[-1], df[col].iloc[-1] * 100),
                xytext=(6, dy), textcoords="offset points", va="center", fontsize=9, color="#191919")
for lim, txt in ((lim_t, "seuil total ±1 %"), (lim_g, "seuil groupes ±2 %")):
    for sign in (1, -1):
        ax.axhline(sign * lim * 100, color="#9c9c9c", linewidth=1, linestyle=(0, (4, 3)))
    ax.text(df.index[0], lim * 100 + 0.04, txt, fontsize=8, color="#666666", va="bottom")
ax.axhline(0, color="#666666", linewidth=0.8)
ax.set_ylabel("Écart relatif moteur / Insee (%)")
ax.set_title("Reproduction de la projection Insee 2026 : écart relatif par année", fontsize=11, loc="left")
ax.set_xlim(df.index[0], df.index[-1] + 9)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.grid(axis="y", color="#e6e6e6", linewidth=0.6)
ax.legend(frameon=False, fontsize=8, loc="lower left", ncol=4)
fig.tight_layout()
(R / "docs" / "figures").mkdir(parents=True, exist_ok=True)
fig.savefig(R / "docs" / "figures" / "ecarts-insee.png")
print("\nGraphique : docs/figures/ecarts-insee.png")
