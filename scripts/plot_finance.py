"""Phase 3, étape 11 : premier bilan financier 2026-2065 (scénario central, réserve initiale k = 0) et perte d'emploi de D16.

Usage :  python scripts/plot_finance.py
Écrit docs/figures/finance-2026-2065.png (six panneaux, dont la perte d'emploi de D16) et
data/processed/finance-central.csv (ignoré par Git). Imprime lambda, tau0 et la perte d'emploi.

Ce ne sont pas des résultats actuariels : tau0 est un taux de calibration, les trajectoires sont
conditionnelles aux hypothèses de docs/hypotheses.md, sans aléa (phase 5).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import _bootstrap
from actuarial_model.model import build_inputs, load_phase3_data, project_population, run_finance
from config import get_param, load_config
from economics.macro import MacroPaths

R = _bootstrap.RACINE
cfg = load_config(R / "config" / "assumptions.yaml")
states = project_population(cfg, R)
data = load_phase3_data(cfg, R)
inp = build_inputs(cfg, states, data)
res = run_finance(cfg, inp, MacroPaths.from_config(cfg, inp.years, n_sim=1), k=get_param(cfg, "finance.initial_reserve_k.reference"))
yrs = res.years

# ---- tableau
out = pd.DataFrame({"annee": yrs, "cotisants": res.contributors[0], "retraites": res.retirees, "ratio": res.ratio[0],
                    "assiette": res.assiette[0], "prestations": res.benefits[0], "cotisations": res.contributions[0],
                    "deficit": res.deficit[0], "reserve_debut": res.reserve[0, :-1], "reserve_fin": res.reserve[0, 1:]})
(R / "data" / "processed").mkdir(parents=True, exist_ok=True)
out.to_csv(R / "data" / "processed" / "finance-central.csv", index=False, float_format="%.6g")
lam = res.diagnostics["lambda"]
print(f"tau0 = {res.tau0:.4f} (taux de calibration, pas un taux légal)")
print(f"lambda = {lam['lambda']:.4f} ; dépense avant {lam['expenditure_before'] / 1e9:.1f} Md€, après {lam['expenditure_after'] / 1e9:.1f} Md€, "
      f"référence {lam['reference_total'] / 1e9:.1f} Md€, écart {lam['gap_percent']:+.2f} %")
show = out.iloc[[0, 1, 5, 10, 15, 20, 25, 30, 35, 39]].copy()
for col in ("cotisants", "retraites"):
    show[col] = (show[col] / 1e6).round(2)
for col in ("assiette", "prestations", "cotisations", "deficit", "reserve_fin"):
    show[col] = (show[col] / 1e9).round(1)
print(show.drop(columns="reserve_debut").to_string(index=False))

# ---- couleurs : une couleur par série, jamais une couleur seule pour porter l'information (étiquettes directes)
BLEU, ORANGE, VERT, OR, GRIS = "#257de0", "#f47230", "#00b894", "#f2a600", "#666666"


def style(ax, title, ylabel):
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_ylabel(ylabel, fontsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.6)
    ax.tick_params(labelsize=8)
    ax.set_xlim(yrs[0], yrs[-1] + 9)


def label_end(ax, x, y, text, color, dy=0):
    ax.annotate(text, (x, y), xytext=(5, dy), textcoords="offset points", va="center", fontsize=8, color="#191919")
    ax.plot([x], [y], marker="o", markersize=3, color=color)


fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.5), dpi=150)
ax = axes[0, 0]
ax.plot(yrs, res.contributors[0] / 1e6, color=BLEU, linewidth=2)
ax.plot(yrs, res.retirees / 1e6, color=ORANGE, linewidth=2)
label_end(ax, yrs[-1], res.contributors[0, -1] / 1e6, "Cotisants", BLEU)
label_end(ax, yrs[-1], res.retirees[-1] / 1e6, "Retraités", ORANGE)
style(ax, "Cotisants et retraités", "millions de personnes")
ax = axes[0, 1]
ax.plot(yrs, res.ratio[0], color=VERT, linewidth=2)
label_end(ax, yrs[-1], res.ratio[0, -1], f"{res.ratio[0, -1]:.2f}", VERT)
style(ax, "Cotisants par retraité", "ratio")
ax = axes[0, 2]
ax.plot(yrs, res.benefits[0] / 1e9, color=ORANGE, linewidth=2)
ax.plot(yrs, res.contributions[0] / 1e9, color=BLEU, linewidth=2)
label_end(ax, yrs[-1], res.benefits[0, -1] / 1e9, "Prestations B", ORANGE)
label_end(ax, yrs[-1], res.contributions[0, -1] / 1e9, "Cotisations C", BLEU)
style(ax, "Prestations et cotisations", "milliards d'euros 2026")
ax = axes[1, 0]
ax.axhline(0, color=GRIS, linewidth=0.8)
ax.bar(yrs, res.deficit[0] / 1e9, color=OR, width=0.8)
style(ax, "Déficit annuel D = B - C (D_2026 = 0 par calibration)", "milliards d'euros 2026")
ax = axes[1, 1]
ax.axhline(0, color=GRIS, linewidth=0.8)
ax.plot(np.append(yrs, yrs[-1] + 1), res.reserve[0] / 1e9, color=BLEU, linewidth=2)
style(ax, f"Réserve R, k = {res.k:g}, rendement réel {get_param(cfg, 'finance.real_return_on_reserves'):.1%}", "milliards d'euros 2026")
ax.set_xlim(yrs[0], yrs[-1] + 2)

# ---- perte d'emploi D16, pour delta - 1, delta, delta + 1
ax = axes[1, 2]
styles = {-1: (ORANGE, "δ − 1 an"), 0: (BLEU, "δ calibré"), 1: (VERT, "δ + 1 an")}
phi_ref = np.ones(inp.n_years)
losses = {}
for shift, (col, lab) in styles.items():
    i2 = build_inputs(cfg, states, data, delta_shift=shift)
    r2 = run_finance(cfg, i2, MacroPaths.from_config(cfg, i2.years, 1))
    losses[shift] = (r2.loss, r2.loss_share)
    ax.plot(yrs, r2.loss_share * 100, color=col, linewidth=2)
    label_end(ax, yrs[-1], r2.loss_share[-1] * 100, lab, col)
style(ax, "Perte d'emploi observé (D16)", "% de l'emploi couvert par le modèle")
fig.tight_layout()
(R / "docs" / "figures").mkdir(parents=True, exist_ok=True)
fig.savefig(R / "docs" / "figures" / "finance-2026-2065.png")
print("\nPerte d'emploi D16 (personnes, part de l'emploi couvert) :")
for shift, (loss, share) in losses.items():
    print(f"delta {shift:+d} : 2026 {loss[0] / 1e3:7.0f} k ({share[0]:.2%})   2045 {loss[19] / 1e3:7.0f} k ({share[19]:.2%})   2065 {loss[-1] / 1e3:7.0f} k ({share[-1]:.2%})")
print("\nGraphique : docs/figures/finance-2026-2065.png")
