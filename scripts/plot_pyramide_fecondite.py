"""Étape 4 : pyramide des âges 2026 et fécondité par âge de la mère (exploration des données).

Usage :  python scripts/plot_pyramide_fecondite.py
Écrit docs/figures/pyramide-2026.png et docs/figures/fecondite-2026.png.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import _bootstrap
from config import get_param, load_config, raw_data_path
from conventions import SEX_F, SEX_M
from data_io.insee import FERTILITY_FIRST_AGE, FERTILITY_LAST_AGE, load_central_projection, load_population_2026

R = _bootstrap.RACINE
cfg = load_config(R / "config" / "assumptions.yaml")
first = get_param(cfg, "horizon.start_year")
n_init = load_population_2026(raw_data_path(cfg, R, "insee_population_file"),
                              get_param(cfg, "data_files.insee_population_sheet"),
                              get_param(cfg, "data_files.insee_population_scope"))
proj = load_central_projection(raw_data_path(cfg, R, "insee_projection_file"))
out = R / "docs" / "figures"
out.mkdir(parents=True, exist_ok=True)

ages = np.arange(n_init.shape[1])
fig, ax = plt.subplots(figsize=(6, 7), dpi=150)
ax.barh(ages, -n_init[SEX_M] / 1e3, color="#f47230", height=0.85, label="Hommes")
ax.barh(ages, n_init[SEX_F] / 1e3, color="#257de0", height=0.85, label="Femmes")
ax.set_xlabel("Effectif au 1er janvier 2026 (milliers)")
ax.set_ylabel("Âge révolu (105 = 105 ans ou plus)")
ax.set_xticks(ax.get_xticks())
ax.set_xticklabels([f"{abs(t):.0f}" for t in ax.get_xticks()])
ax.set_title("Pyramide des âges, France, 1er janvier 2026", loc="left", fontsize=11)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig(out / "pyramide-2026.png")

i = proj.year_index(first)
fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
a = np.arange(FERTILITY_FIRST_AGE, FERTILITY_LAST_AGE + 1)
ax.plot(a, proj.fertility[:, i] * 1e4, color="#257de0", linewidth=2)
ax.set_xlabel("Âge atteint dans l'année")
ax.set_ylabel("Naissances pour 10 000 femmes")
ax.set_title(f"Taux de fécondité par âge de la mère, {first} (scénario central)", loc="left", fontsize=11)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.grid(axis="y", color="#e6e6e6", linewidth=0.6)
fig.tight_layout()
fig.savefig(out / "fecondite-2026.png")
print("Graphiques écrits dans docs/figures/")
