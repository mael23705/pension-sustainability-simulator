"""Bilan annuel et vectorisation sur l'axe des simulations (étapes 8 et 9 de la phase 3)."""
import numpy as np
import pytest

from actuarial_model import finance
from actuarial_model.model import build_inputs, run_finance
from economics.macro import MacroPaths
from helpers import toy_finance_setup

TOL = 1e-9


def test_identite_du_bilan_et_signe():
    d = np.array([[0.0, 10.0, -5.0], [1.0, 2.0, 3.0]])
    r = np.full(d.shape, 0.05)
    R = finance.reserves(np.array([100.0, 0.0]), d, r)
    assert R.shape == (2, 4)
    assert R[:, 1:] == pytest.approx(R[:, :-1] * 1.05 - d, abs=TOL)
    assert R[0, 1] == pytest.approx(105.0, abs=TOL)                 # D = 0 : la réserve ne fait que rapporter
    assert R[1, 1] == pytest.approx(-1.0, abs=TOL)                  # k = 0 et D > 0 : réserve négative


def test_k_nul_et_deficit_nul_donne_reserve_nulle():
    R = finance.reserves(0.0, np.zeros((1, 5)), np.full((1, 5), 0.01))
    assert np.all(R == 0.0)


def test_formes_incoherentes_refusees():
    with pytest.raises(ValueError):
        finance.reserves(0.0, np.zeros((2, 5)), np.zeros((2, 4)))


def test_deficit_et_cotisations():
    assert finance.contributions(0.25, np.array([100.0, 200.0])).tolist() == [25.0, 50.0]
    assert finance.deficit(np.array([100.0]), np.array([60.0]), 10.0).tolist() == [30.0]


@pytest.fixture(scope="module")
def toy(cfg):
    toy_cfg, states, data, paths = toy_finance_setup(cfg)
    return toy_cfg, build_inputs(toy_cfg, states, data), paths


def tile(paths: MacroPaths, n: int) -> MacroPaths:
    t = lambda a: np.tile(a, (n, 1))
    return MacroPaths(t(paths.productivity_growth), t(paths.unemployment), t(paths.real_return))


def test_trois_simulations_identiques_trois_trajectoires_identiques(toy):
    cfg, inp, paths = toy
    res = run_finance(cfg, inp, tile(paths, 3), k=0.5)
    for arr in (res.assiette, res.benefits, res.contributions, res.deficit, res.reserve, res.contributors):
        assert arr[1] == pytest.approx(arr[0], abs=TOL) and arr[2] == pytest.approx(arr[0], abs=TOL)
    single = run_finance(cfg, inp, paths, k=0.5)
    assert res.reserve[0] == pytest.approx(single.reserve[0], abs=TOL)


def test_seul_r_different_seul_r_change(toy):
    cfg, inp, paths = toy
    p3 = tile(paths, 3)
    r = p3.real_return.copy()
    r[1] += 0.03
    r[2] -= 0.02
    res = run_finance(cfg, inp, p3.with_real_return(r), k=0.5)
    base = run_finance(cfg, inp, tile(paths, 1), k=0.5)
    for name in ("assiette", "benefits", "contributions", "deficit", "contributors"):
        assert getattr(res, name)[1] == pytest.approx(getattr(base, name)[0], abs=TOL)
        assert getattr(res, name)[2] == pytest.approx(getattr(base, name)[0], abs=TOL)
    assert res.reserve[1, 1] != pytest.approx(res.reserve[0, 1], abs=1e-6)       # k > 0 : le rendement joue dès 2027
    assert res.reserve[0] == pytest.approx(base.reserve[0], abs=TOL)


def test_productivite_differente_change_assiette_et_prestations_des_nouveaux_liquidants(toy):
    cfg, inp, paths = toy
    p2 = tile(paths, 2)
    g = p2.productivity_growth.copy()
    g[1, 1] = 0.20                                                     # +20 % au lieu de +10 % en 2027
    res = run_finance(cfg, inp, MacroPaths(g, p2.unemployment, p2.real_return), k=0.0)
    assert res.assiette[1, 1] == pytest.approx(res.assiette[0, 1] * 1.2 / 1.1, abs=TOL)
    # toute la classe 2+ de 2027 est « nouvelle » dans le cas jouet : B suit G
    assert res.benefits[1, 1] == pytest.approx(res.benefits[0, 1] * 1.2 / 1.1, abs=TOL)
    assert res.deficit[:, 0] == pytest.approx([0.0, 0.0], abs=TOL)      # 2026 commun : D_2026 = 0 pour toutes


def test_donnees_de_2026_differentes_entre_simulations_refusees(toy):
    from config import ConfigError
    cfg, inp, paths = toy
    p2 = tile(paths, 2)
    u = p2.unemployment.copy()
    u[1, 0] = 0.05
    with pytest.raises(ConfigError, match="D_2026"):
        run_finance(cfg, inp, MacroPaths(p2.productivity_growth, u, p2.real_return), k=0.0)


def test_chomage_trop_bas_fait_echouer_le_test_t11(toy):
    from economics.employment import EmploymentError
    cfg, inp, paths = toy
    u = paths.unemployment.copy()
    u[0, 1] = 0.0                       # phi = 1/0,9 : e = 0,8 x 1,11 = 0,89 : encore valide
    run_finance(cfg, inp, MacroPaths(paths.productivity_growth, u, paths.real_return), k=0.0)
    cfg2 = __import__("copy").deepcopy(cfg)
    cfg2["macro"]["unemployment_rate_2025"] = {"value": 0.5}           # phi = 0,9/0,5 : e = 0,8 x 1,9 > 1
    with pytest.raises(EmploymentError):
        run_finance(cfg2, inp, paths, k=0.0)


def test_k_proportionnel_a_b_2026(toy):
    cfg, inp, paths = toy
    r0 = run_finance(cfg, inp, paths, k=0.0).reserve[0, 0]
    r1 = run_finance(cfg, inp, paths, k=2.0).reserve[0, 0]
    assert r0 == 0.0 and r1 == pytest.approx(2.0 * 1200.0, abs=TOL)
