"""Vérifications indépendantes du moteur financier : des boucles explicites, lentes et naïves, recalculent
ce que le code vectorisé calcule d'un seul coup (cotisants D16, pensions du stock et des nouveaux liquidants).

Ces tests ont été ajoutés après un contrôle par mutations : retirer (1 - rho) des cotisants, mal indexer la matrice
des nouveaux liquidants ou inverser les sexes de delta passait tous les premiers tests.
Cas jouet : valeurs de test uniquement (aucun résultat présenté). Les cas sur données réelles sont ignorés si les données manquent.
"""
import copy
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from actuarial_model import calibration as cal
from actuarial_model.model import build_inputs, load_phase3_data, project_population
from actuarial_model.retirement import legal_age
from config import get_param
from economics import macro
from helpers import toy_finance_setup

ROOT = Path(__file__).resolve().parent.parent
TOL = 1e-9


def slow_reference(cfg, inp, e_obs_scaled, growth_index):
    """Recalcule cotisants, B_stock et B_new par boucles explicites. Renvoie (K[t], Bstock[t], Bnew[t])."""
    T, C, S, K = inp.n.shape
    first, a0 = int(inp.years[0]), int(inp.ages[0])
    tol = float(get_param(cfg, "tests.conservation_tolerance"))
    contributors, bstock, bnew = np.zeros(T), np.zeros(T), np.zeros(T)
    for t in range(T):
        for s in range(S):
            for k in range(K):
                age = a0 + k
                g = int(inp.years[t]) - age
                a_star = [legal_age(g, cfg) + int(inp.delta[c, s]) for c in range(C)]
                ret = [1.0 if age >= a_star[c] else 0.0 for c in range(C)]
                tot = sum(inp.n[t, c, s, k] for c in range(C))
                rb = sum(inp.n[t, c, s, k] * ret[c] for c in range(C)) / tot if tot > 0 else 1.0
                e = 0.0 if 1.0 - rb <= tol else e_obs_scaled[s, k] / (1.0 - rb)
                for c in range(C):
                    contributors[t] += inp.n[t, c, s, k] * (1.0 - ret[c]) * e
                    if ret[c] == 0.0:
                        continue
                    t_g = g + a_star[c] - first
                    if t_g <= 0:          # déjà retraitée en 2026 : stock, pension à l'âge de 2026
                        k0 = min(max(age - t - a0, 0), K - 1)
                        bstock[t] += inp.n[t, c, s, k] * inp.pension_stock[c, s, k0]
                    else:                 # part en t_g : pension theta x w(a*) x G(t_g)
                        k_dep = min(max(a_star[c] - a0, 0), K - 1)
                        bnew[t] += inp.n[t, c, s, k] * inp.theta[c, s] * inp.wages[c, s, k_dep] * growth_index[t_g]
    return contributors, bstock, bnew


@pytest.fixture(scope="module")
def toy3(cfg):
    """Cas jouet sur 3 ans avec delta = -1 pour le public et les indépendants : des générations partent avant l'année courante."""
    toy_cfg, states, data, paths = toy_finance_setup(cfg, flow_years=3)
    low = np.array([[0.0, 0.1, 0.4], [0.0, 0.1, 0.4]])      # emploi observé bas : e conditionnel reste dans [0, 1] malgré delta = -1
    data = replace(data, profile=replace(data.profile, e_obs=low))
    delta = np.array([[0, 0], [-1, -1], [-1, 0]])
    inp = build_inputs(toy_cfg, states, data, delta=delta)
    return toy_cfg, inp, data


def test_cas_jouet_cotisants_stock_et_nouveaux_liquidants(toy3):
    cfg, inp, data = toy3
    G = macro.wage_index(np.array([0.0, 0.10, 0.05]))
    e_scaled = data.profile.e_obs[:, int(inp.ages[0]):]
    K_slow, bs_slow, bn_slow = slow_reference(cfg, inp, e_scaled, G)
    assert inp.contributors_base == pytest.approx(K_slow, abs=TOL)
    assert inp.benefits_stock == pytest.approx(bs_slow, abs=TOL)
    assert G @ inp.new_matrix == pytest.approx(bn_slow, abs=TOL)
    assert (G @ inp.new_matrix)[2] > 0 and inp.new_matrix[1, 2] > 0 and inp.new_matrix[2, 2] > 0    # générations parties en 2027 et en 2028


def test_cas_jouet_somme_des_cotisants_egale_emploi_observe_hors_cellules_retraitees(toy3):
    """D16 avec des delta différents selon la catégorie : rho_bar intermédiaire, somme_c N (1 - rho) e = N e_obs."""
    cfg, inp, data = toy3
    e_obs = data.profile.e_obs[:, int(inp.ages[0]):]
    cell_contrib = (inp.n * (1.0 - inp.rho) * inp.e_base[:, None]).sum(axis=1)       # (T, S, K)
    cell_n = inp.n.sum(axis=1)
    partial = (inp.rho_bar > 0) & (inp.rho_bar < 1)
    assert partial.any()                                         # le cas intermédiaire est bien présent
    expected = cell_n * e_obs[None]
    ok = inp.rho_bar < 1
    assert cell_contrib[ok] == pytest.approx(expected[ok], abs=TOL)
    assert np.all(cell_contrib[~ok] == 0.0)


def test_delta_homme_femme_non_inverses(cfg):
    asym = copy.deepcopy(cfg)
    asym["retirement"]["delta_effective_minus_legal"]["value"] = {
        "prive": {"F": 2, "H": 1}, "public": {"F": 0, "H": -1}, "independants": {"F": 3, "H": 0}}
    assert cal.delta_from_config(asym).tolist() == [[2, 1], [0, -1], [3, 0]]


def test_donnees_reelles_boucles_lentes(cfg):
    need = [ROOT / "data" / "raw" / "3_Pop1janv_age.xlsx", ROOT / "data" / "raw" / "00_central.xlsx",
            ROOT / "data" / "processed" / "eacr-stock-2024.csv", ROOT / "data" / "processed" / "eacr-nouveaux-liquidants-2024.csv",
            ROOT / "data" / "processed" / "taux-emploi-age-sexe-2025.csv"]
    if not all(p.exists() for p in need):
        pytest.skip("Données brutes ou tables dérivées absentes (ignorées par Git).")
    states = project_population(cfg, ROOT)
    data = load_phase3_data(cfg, ROOT)
    inp = build_inputs(cfg, states, data)
    f = float(get_param(cfg, "employment.observed_employment_rate.scale_factor"))
    e_scaled = data.profile.e_obs[:, int(inp.ages[0]):] * f
    rng = np.random.default_rng(7)
    G = macro.wage_index(np.concatenate([[0.0], rng.uniform(-0.01, 0.03, size=inp.n_years - 1)]))
    K_slow, bs_slow, bn_slow = slow_reference(cfg, inp, e_scaled, G)
    assert inp.contributors_base == pytest.approx(K_slow, rel=1e-12)
    assert inp.benefits_stock == pytest.approx(bs_slow, rel=1e-12)
    assert G @ inp.new_matrix == pytest.approx(bn_slow, rel=1e-12)
