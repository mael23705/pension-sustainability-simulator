"""Phase 3 : recalcule et publie les calibrations (delta, kappa, facteur d'échelle, lambda, theta, tau0).

Usage :  python scripts/calibrate_phase3.py
Vérifie aussi que les valeurs saisies dans config/assumptions.yaml (delta, facteur d'échelle) sont
celles que donnent les données. Code de sortie 1 en cas d'écart. Nécessite data/processed/ (scripts
build_employment_table.py et build_eacr_tables.py) et data/raw/ (Insee).
"""
import sys

import numpy as np

import _bootstrap
from actuarial_model import calibration as cal
from actuarial_model.model import build_inputs, load_phase3_data, project_population
from config import categories, get_param, load_config
from economics import employment as emp

R = _bootstrap.RACINE
cfg = load_config(R / "config" / "assumptions.yaml")
data = load_phase3_data(cfg, R)
cats = categories(cfg)
ok = True

print("== delta_{c,s} (D19) ==")
d = cal.calibrate_delta(cfg, data.new_eff, int(get_param(cfg, "retirement.delta_effective_minus_legal.calibration_year")))
print(f"âge légal moyen des liquidants de 2024 : F {d['legal_mean'][0]:.3f}  H {d['legal_mean'][1]:.3f}")
yaml_delta = cal.delta_from_config(cfg)
for c, name in enumerate(cats):
    print(f"{name:<13} réel F {d['real'][c, 0]:+.2f}  H {d['real'][c, 1]:+.2f}   entier F {d['integer'][c, 0]:+d}  H {d['integer'][c, 1]:+d}")
if not np.array_equal(d["integer"], yaml_delta):
    ok = False
    print("ÉCART : le YAML contient", yaml_delta.tolist(), "au lieu de", d["integer"].tolist())

print("\n== facteur d'échelle de l'emploi (D6) ==")
f = emp.scale_factor(data.profile.survey_employment, float(get_param(cfg, "employment.observed_employment_rate.national_accounts_total")))
f_yaml = float(get_param(cfg, "employment.observed_employment_rate.scale_factor"))
print(f"emploi de l'enquête {data.profile.survey_employment / 1e6:.3f} millions ; facteur {f:.5f} (YAML : {f_yaml})")
if abs(f - f_yaml) > 5e-5:
    ok = False
    print("ÉCART : facteur d'échelle du YAML différent du calcul.")

print("\n== kappa_{c,s} (D17) ==")
print(np.round(cal.kappa_from_drees(cfg), 4))

print("\n== lambda, theta, tau0 (D17, D20) ==")
states = project_population(cfg, R)
inp = build_inputs(cfg, states, data)
lam = inp.diagnostics["lambda"]
print(f"lambda = {lam['lambda']:.4f} ; dépense du moteur avant recalage {lam['expenditure_before'] / 1e9:.1f} Md€ ; "
      f"après {lam['expenditure_after'] / 1e9:.1f} Md€ ; référence {lam['reference_total'] / 1e9:.1f} Md€ ; écart avant recalage {lam['gap_percent']:+.2f} %")
print(f"retraités du moteur en 2026 : {inp.diagnostics['retired_2026'] / 1e6:.2f} millions ; EACR (ligne Ensemble) : "
      f"{inp.diagnostics['retired_observed_eacr'] / 1e6:.2f} millions")
print("theta (apparent) :", np.round(inp.diagnostics["theta"], 3).tolist())
sys.exit(0 if ok else 1)
