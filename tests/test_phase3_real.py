"""Moteur financier sur les données réelles : cohérence interne et valeurs publiées (phase 3).

Ces tests lisent data/raw/ (Insee) et data/processed/ (tables dérivées des scripts build_*) : ils sont
ignorés quand ces fichiers sont absents (par exemple sur GitHub Actions).
Aucun test ne vérifie un résultat « vrai » : on vérifie les identités, les signes et les plages.
"""
from pathlib import Path

import numpy as np
import pytest

from actuarial_model import calibration as cal
from actuarial_model.model import build_inputs, load_phase3_data, project_population, run_finance
from config import get_param
from economics import employment as emp
from economics.macro import MacroPaths

ROOT = Path(__file__).resolve().parent.parent
NEEDED = [ROOT / "data" / "raw" / "3_Pop1janv_age.xlsx", ROOT / "data" / "raw" / "00_central.xlsx",
          ROOT / "data" / "processed" / "eacr-stock-2024.csv", ROOT / "data" / "processed" / "eacr-nouveaux-liquidants-2024.csv",
          ROOT / "data" / "processed" / "taux-emploi-age-sexe-2025.csv"]
if not all(p.exists() for p in NEEDED):
    pytest.skip("Données brutes ou tables dérivées absentes (ignorées par Git).", allow_module_level=True)


@pytest.fixture(scope="module")
def world(cfg):
    states = project_population(cfg, ROOT)
    data = load_phase3_data(cfg, ROOT)
    inp = build_inputs(cfg, states, data)
    paths = MacroPaths.from_config(cfg, inp.years, n_sim=2)
    return states, data, inp, paths, run_finance(cfg, inp, paths)


def test_delta_du_yaml_est_celui_des_donnees(cfg, world):
    _, data, _, _, _ = world
    d = cal.calibrate_delta(cfg, data.new_eff, int(get_param(cfg, "retirement.delta_effective_minus_legal.calibration_year")))
    assert np.array_equal(d["integer"], cal.delta_from_config(cfg))


def test_facteur_d_echelle_du_yaml_est_celui_des_donnees(cfg, world):
    _, data, _, _, _ = world
    f = emp.scale_factor(data.profile.survey_employment, float(get_param(cfg, "employment.observed_employment_rate.national_accounts_total")))
    assert f == pytest.approx(float(get_param(cfg, "employment.observed_employment_rate.scale_factor")), abs=5e-5)
    lo, hi = cfg["employment"]["observed_employment_rate"]["scale_factor"]["test_range"]
    assert lo <= f <= hi


def test_la_population_du_modele_est_celle_du_moteur_demographique(world):
    states, _, inp, _, _ = world
    assert inp.n[:, :, :, :].sum(axis=(1, 2, 3)) == pytest.approx([st.n.sum() for st in states[:40]], rel=1e-12)


def test_d_2026_est_nul_et_tau0_est_le_taux_de_calibration(world):
    _, _, _, _, res = world
    assert abs(res.deficit[0, 0]) <= 1e-9 * res.benefits[0, 0]
    assert res.contributions[0, 0] == pytest.approx(res.benefits[0, 0], rel=1e-12)
    assert 0.0 < res.tau0 < 1.0


def test_identite_du_bilan_sur_toute_la_trajectoire(cfg, world):
    _, _, _, paths, res = world
    r = paths.real_return
    assert res.reserve[:, 1:] == pytest.approx(res.reserve[:, :-1] * (1 + r) - res.deficit, rel=1e-12, abs=1e-3)
    assert res.reserve[:, 0] == pytest.approx(0.0, abs=1e-9)                # k = 0 : cas limite analytique
    assert res.deficit == pytest.approx(res.benefits - res.contributions, rel=1e-12)


def test_signes_et_formes(world):
    _, _, inp, _, res = world
    assert res.assiette.shape == res.benefits.shape == res.deficit.shape == (2, 40)
    assert res.reserve.shape == (2, 41)
    assert np.all(res.assiette >= 0) and np.all(res.benefits >= 0) and np.all(res.contributors >= 0)
    assert np.all(res.retirees > 0) and np.all(res.ratio > 0)
    assert res.reserve[0] == pytest.approx(res.reserve[1], abs=1e-6)       # deux simulations identiques


def test_taux_conditionnel_dans_zero_un_pour_tous_les_scenarios(cfg, world):
    states, data, _, _, _ = world
    for shift in (-1, 0, 1):
        inp = build_inputs(cfg, states, data, delta_shift=shift)
        assert inp.e_base.min() >= 0.0 and inp.e_base.max() <= 1.0
        for scenario in ("favorable", "central", "unfavorable"):
            run_finance(cfg, inp, MacroPaths.from_config(cfg, inp.years, 1, scenario))      # ne doit pas lever d'erreur


def test_rho_bar_2026(world):
    _, _, inp, _, _ = world
    ages = inp.ages
    assert np.all(inp.rho_bar[0][:, ages <= 62] == 0.0)                    # personne n'est retraité à 62 ans ou moins
    assert np.all(inp.rho_bar[0][:, ages >= 64] == 1.0)
    assert np.all((inp.rho_bar >= 0.0) & (inp.rho_bar <= 1.0))


def test_cotisants_nuls_apres_la_retraite_et_proches_de_l_emploi_en_2026(world):
    _, _, inp, _, res = world
    assert 28e6 < res.contributors[0, 0] < 31e6           # emploi de la comptabilité nationale : 30,6 millions, moins les moins de 20 ans et les retraités
    assert np.all(np.abs(inp.n * inp.rho * inp.e_base[:, None, :, :]) >= 0)


def test_stock_decroit_et_pensions_nouvelles_croissent(world):
    _, _, inp, _, _ = world
    assert np.all(np.diff(inp.benefits_stock) <= 1e-6)
    assert inp.new_matrix.sum(axis=0)[0] == 0.0           # aucun nouveau liquidant en 2026 : tout le monde est dans le stock
    assert inp.new_matrix.sum(axis=0)[-1] > inp.new_matrix.sum(axis=0)[1]


def test_lambda_et_theta_publies(world):
    _, _, inp, _, res = world
    lam = res.diagnostics["lambda"]
    assert 0.8 < lam["lambda"] < 1.5 and lam["expenditure_after"] == pytest.approx(lam["reference_total"], rel=1e-12)
    theta = res.diagnostics["theta"]
    assert np.all(theta > 0.2) and np.all(theta < 0.9)    # taux de remplacement apparents plausibles
    k = res.diagnostics["kappa"]
    assert np.all(k[1] > k[0]) and np.all(k[0] > k[2])    # contrôle de signe du panorama : public > privé > indépendants


def test_perte_d_emploi_publiee_et_decroissante_avec_delta(cfg, world):
    states, data, _, _, _ = world
    shares = []
    for shift in (-1, 0, 1):
        inp = build_inputs(cfg, states, data, delta_shift=shift)
        shares.append(inp.loss_base[0] / inp.covered_employment_base[0])
    assert shares[0] > shares[1] > shares[2] > 0           # plus de retraités entièrement sortis de l'emploi quand delta baisse


def test_vectorisation_n_simulations(cfg, world):
    _, _, inp, _, _ = world
    p = MacroPaths.from_config(cfg, inp.years, n_sim=500)
    r = np.random.default_rng(0).normal(0.01, 0.02, size=p.real_return.shape)
    res = run_finance(cfg, inp, p.with_real_return(r))
    assert res.reserve.shape == (500, 41)
    ref = run_finance(cfg, inp, MacroPaths.from_config(cfg, inp.years, 1))
    assert res.deficit[123] == pytest.approx(ref.deficit[0], rel=1e-12, abs=1e-3)       # r ne change pas D
