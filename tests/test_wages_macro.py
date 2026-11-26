"""Salaires (D7 à D10) et trajectoires macroéconomiques (D18)."""
import numpy as np
import pytest

from config import ConfigError
from economics import macro, wages

AGES = np.arange(20, 101)


def test_inflation_cumulee(cfg):
    assert wages.price_factor(cfg, 2024) == pytest.approx(1.009 * 1.019, abs=1e-12)
    assert wages.price_factor(cfg, 2022) == pytest.approx(1.049 * 1.020 * 1.009 * 1.019, abs=1e-12)
    assert wages.price_factor(cfg, 2026) == 1.0


def test_fonction_en_escalier():
    out = wages.step_function([0, 25, 40], [10.0, 20.0, 30.0], np.array([20, 24, 25, 39, 40, 99]))
    assert out.tolist() == [10.0, 10.0, 20.0, 20.0, 30.0, 30.0]
    with pytest.raises(ConfigError):
        wages.step_function([0, 40, 25], [1.0, 2.0, 3.0], np.array([30]))


def test_salaire_prive_brut_annuel(cfg):
    w = wages.annual_gross_wages(cfg, AGES)
    prive = cfg["wages"]["private"]["net_monthly_euros"]
    # femme de 30 ans (tranche 25-39), privé : net x 1,318 x prix 2024-2026 x 12
    expected = prive["F"][1] * 1.318 * (1.009 * 1.019) * 12
    assert w[0, 0, 30 - 20] == pytest.approx(expected, rel=1e-12)
    # au-delà de 55 ans : dernière tranche conservée (D9)
    assert w[0, 1, 62 - 20] == w[0, 1, 99 - 20] == pytest.approx(prive["H"][4] * 1.318 * (1.009 * 1.019) * 12, rel=1e-12)


def test_ecart_de_sexe_public_et_independants(cfg):
    w = wages.annual_gross_wages(cfg, AGES)
    pub = cfg["wages"]["public"]["sex_means_net_monthly"]
    assert w[1, 1, 40] / w[1, 0, 40] == pytest.approx(pub["H"] / pub["F"], rel=1e-12)
    ind = cfg["wages"]["independents"]["sex_means_net_monthly"]
    assert w[2, 1, 40] / w[2, 0, 40] == pytest.approx(ind["H"] / ind["F"], rel=1e-12)


def test_public_est_la_moyenne_ponderee_des_trois_fonctions_publiques(cfg):
    net = wages.net_monthly_by_category(cfg, AGES)
    blk = cfg["wages"]["public"]
    wt = blk["sub_sector_weights"]
    band = 3                                   # 50-59 ans
    expected = sum(wt[k] * blk["net_monthly_euros"][k][band] for k in wt)
    ratio = blk["sex_means_net_monthly"]["F"] / blk["sex_means_net_monthly"]["all"]
    assert net[1, 0, 55 - 20] == pytest.approx(expected * ratio, rel=1e-12)


def test_salaires_positifs(cfg):
    assert np.all(wages.annual_gross_wages(cfg, AGES) > 0)


def test_transition_lineaire():
    years = np.arange(2026, 2046)
    out = macro.linear_transition(0.079, 0.07, 2026, 2040, years)
    assert out[0] == pytest.approx(0.079)
    assert out[14] == pytest.approx(0.07) and out[-1] == pytest.approx(0.07)
    assert out[7] == pytest.approx(0.0745)
    assert np.all(np.diff(out) <= 1e-15)


def test_trajectoires_du_yaml(cfg):
    years = np.arange(2026, 2066)
    u = macro.unemployment_path(cfg, years)
    g = macro.productivity_path(cfg, years)
    assert u[0] == pytest.approx(0.079) and u[-1] == pytest.approx(0.07)
    assert np.allclose(g, 0.007)                         # g_2026 = cible : transition plate (D18, option A)
    uf = macro.unemployment_path(cfg, years, "favorable")
    uu = macro.unemployment_path(cfg, years, "unfavorable")
    assert uf[-1] == pytest.approx(0.05) and uu[-1] == pytest.approx(0.10)
    with pytest.raises(ConfigError):
        macro.long_term_values(cfg, "inconnu")


def test_indice_des_salaires():
    g = np.array([[0.5, 0.1, 0.1], [0.5, 0.0, 0.2]])
    G = macro.wage_index(g)
    assert G[:, 0].tolist() == [1.0, 1.0]              # la croissance de la première année n'intervient pas
    assert G[0] == pytest.approx([1.0, 1.1, 1.21], abs=1e-12)
    assert G[1] == pytest.approx([1.0, 1.0, 1.2], abs=1e-12)
    assert g[0, 0] == 0.5                              # l'entrée n'est pas modifiée


def test_macro_paths_forme_et_validation(cfg):
    years = np.arange(2026, 2066)
    p = macro.MacroPaths.from_config(cfg, years, n_sim=4)
    assert p.n_sim == 4 and p.n_years == 40
    assert p.real_return.shape == (4, 40) and np.all(p.real_return == 0.01)
    assert p.reference().n_sim == 1
    with pytest.raises(ValueError):
        macro.MacroPaths(np.zeros((2, 3)), np.zeros((2, 4)), np.zeros((2, 3)))
