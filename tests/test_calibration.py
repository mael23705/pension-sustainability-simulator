"""Calibrations : kappa, lambda, theta, delta, tau0 (D17, D19, D20)."""
import numpy as np
import pytest

from actuarial_model import calibration as cal
from config import ConfigError


def test_arrondi_au_plus_proche_demi_vers_le_haut():
    assert cal.round_half_up([0.4, 0.5, 1.28, 1.5, 2.49, -0.5]).tolist() == [0, 1, 1, 2, 2, 0]


def test_kappa_calcule_a_la_main_a_partir_des_tableaux_drees(cfg):
    k = cal.kappa_from_drees(cfg)
    # privé, femmes : (6640 x 1200 + 210 x 1430) / (6640 + 210) / 1380
    assert k[0, 0] == pytest.approx((6640 * 1200 + 210 * 1430) / 6850 / 1380, rel=1e-12)
    # public, hommes : (660 x 2820 + 320 x 2330 + 340 x 2050 + 370 x 2840) / 1690 / 2190
    assert k[1, 1] == pytest.approx((660 * 2820 + 320 * 2330 + 340 * 2050 + 370 * 2840) / 1690 / 2190, rel=1e-12)
    # indépendants : autre régime de non-salariés seul
    assert k[2, 0] == pytest.approx(1070 / 1380, rel=1e-12)
    # ordre de signe du panorama : public > privé > indépendants, pour chaque sexe
    assert np.all(k[1] > k[0]) and np.all(k[0] > k[2])


def test_kappa_categorie_sans_regime_est_une_erreur(cfg):
    import copy
    bad = copy.deepcopy(cfg)
    for r in bad["pensions"]["stock_breakdown"]["drees_table_3_4"]["regimes"].values():
        if r["category"] == "independants":
            r["category"] = "prive"
    with pytest.raises(ConfigError):
        cal.kappa_from_drees(bad)


def test_lambda_et_diagnostics():
    d = cal.calibrate_lambda(b_obs=120.0, b_initial=100.0)
    assert d["lambda"] == pytest.approx(1.2, abs=1e-15)
    assert d["expenditure_after"] == pytest.approx(120.0, abs=1e-12)
    assert d["gap_percent"] == pytest.approx(-100.0 * 20.0 / 120.0, abs=1e-12)
    with pytest.raises(ConfigError):
        cal.calibrate_lambda(0.0, 100.0)


def test_tau0_ferme_et_erreur():
    assert cal.calibrate_tau0(300.0, 1200.0) == pytest.approx(0.25, abs=1e-15)
    assert cal.calibrate_tau0(300.0, 1200.0) * 1200.0 == pytest.approx(300.0, abs=1e-12)    # tau A = B
    with pytest.raises(ConfigError):
        cal.calibrate_tau0(300.0, 0.0)


def test_stock_pension_table_et_depense_observee():
    m1 = np.array([[0.0, 100.0, 200.0], [0.0, 120.0, 240.0]])
    kappa = np.array([[1.0, 1.0], [2.0, 0.5]])
    p = cal.stock_pension_table(m1, kappa, advance=1.1, months=12, a0=1)
    assert p.shape == (2, 2, 2)
    assert p[1, 1, 1] == pytest.approx(12 * 1.1 * 0.5 * 240.0, abs=1e-9)
    eff = np.array([[0.0, 10.0, 20.0], [0.0, 5.0, 5.0]])
    b = cal.observed_stock_expenditure(eff, m1, d13_factor=1.01, advance=1.1, months=12)
    assert b == pytest.approx(12 * 1.1 * 1.01 * (10 * 100 + 20 * 200 + 5 * 120 + 5 * 240), abs=1e-9)


def test_theta_continuite_avec_le_stock():
    """theta x salaire de départ = pension annuelle des nouveaux liquidants de la catégorie (même chaîne que le stock)."""
    eff = np.array([[0.0, 10.0], [0.0, 30.0]])
    m1 = np.array([[0.0, 800.0], [0.0, 1000.0]])
    kappa = np.array([[1.0, 1.0], [2.0, 0.5]])
    w_bar = np.array([[24000.0, 30000.0], [36000.0, 36000.0]])
    theta = cal.calibrate_theta(eff, m1, kappa, lam=1.1, advance=1.02, months=12, w_bar=w_bar)
    assert theta[1, 1] * w_bar[1, 1] == pytest.approx(12 * 1.02 * 1.1 * 0.5 * 1000.0, abs=1e-9)
    assert theta[0, 0] == pytest.approx(12 * 1.02 * 1.1 * 800.0 / 24000.0, abs=1e-12)
    with pytest.raises(ConfigError):
        cal.calibrate_theta(eff * 0, m1, kappa, 1.1, 1.02, 12, w_bar)


def test_age_legal_moyen_des_liquidants(cfg):
    eff = np.zeros((2, 101))
    eff[:, 62] = [10.0, 10.0]          # génération 1962 en 2024 : âge légal 63 (62,5 arrondi vers le haut)
    eff[:, 63] = [30.0, 10.0]          # génération 1961 : 62
    out = cal.mean_legal_age_of_liquidants(eff, 2024, cfg)
    assert out == pytest.approx([(10 * 63 + 30 * 62) / 40, 62.5], abs=1e-12)


def test_delta_vaut_age_effectif_moins_age_legal(cfg):
    eff = np.zeros((2, 101))
    eff[:, 63] = 1.0                   # génération 1961 : âge légal entier 62
    d = cal.calibrate_delta(cfg, eff, 2024)
    # privé : 63,70 - 62 et 63,50 - 62 ; public : 62,9 - 62 ; indépendants : valeur provisoire du YAML
    assert d["real"][0] == pytest.approx([1.70, 1.50], abs=1e-9)
    assert d["real"][1] == pytest.approx([0.90, 0.90], abs=1e-9)
    assert d["real"][2] == pytest.approx([0.0, 0.0], abs=1e-12)
    assert d["integer"].tolist() == [[2, 2], [1, 1], [0, 0]]


def test_delta_du_yaml_et_decalage(cfg):
    d0 = cal.delta_from_config(cfg)
    assert d0.shape == (3, 2) and d0.dtype.kind == "i"
    assert np.array_equal(cal.delta_from_config(cfg, 1), d0 + 1)
    assert np.array_equal(cal.delta_from_config(cfg, -1), d0 - 1)
