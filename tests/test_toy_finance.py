"""Cas jouet financier (phase 3), calculé à la main : le moteur doit le reproduire à 1e-9.

Valeurs d'entrée : bloc `toy_finance` du YAML (statut toy_example). Population : cas jouet de la phase 2,
années 2026 et 2027, âges 1 et 2+ (classe ouverte), trois catégories, pi = (0,5 ; 0,3 ; 0,2).
Retraite : à partir de l'âge 2 (classe ouverte) pour toutes les générations, delta = 0.

Calcul à la main (euros du cas jouet). Notation : p = privé, u = public, i = indépendants ; F, H.
Salaires annuels bruts constants : privé F 100, H 120 ; public F 90, H 110 ; indépendants F 72, H 88.
Taux d'emploi observé à l'âge 1 : F 0,5, H 0,8 ; la classe 2+ est entièrement retraitée (rho_bar = 1), donc e = 0.

2026 (chômage = chômage de référence, phi = 1, G = 1)
  cotisants : F (50 + 20 + 10) x 0,5 = 40 ; H (30 + 30 + 30) x 0,8 = 72 ; total 112.
  A_2026 = 0,5 x (50 x 100 + 20 x 90 + 10 x 72) + 0,8 x (30 x 120 + 30 x 110 + 30 x 88)
         = 0,5 x 7520 + 0,8 x 9540 = 3760 + 7632 = 11392.
  Retraités : classe 2+ : F 20 + 30 + 10, H 10 + 30 + 10, total 110.
  Pension du stock avant recalage : m1 x kappa avec kappa = (1 ; 2 ; 0,5) :
    F : 10 x (20 x 1 + 30 x 2 + 10 x 0,5) = 850 ; H : 12 x (10 x 1 + 30 x 2 + 10 x 0,5) = 900 ; B_initial = 1750.
  B_obs = 60 x 10 + 50 x 12 = 1200 ; lambda = 1200 / 1750 = 24/35 ; B_2026 = 1200.
  tau0 = 1200 / 11392 = 75/712 ; C_2026 = 1200, D_2026 = 0.
2027 (u = 5 %, u_2025 = 10 % : phi = 0,95 / 0,90 ; productivité +10 % : G = 1,1)
  effectifs de l'âge 1 : F (43 ; 25,8 ; 17,2), H (47 ; 28,2 ; 18,8) (calcul à la main de test_toy_example).
  base des salaires : 0,5 x (43 x 100 + 25,8 x 90 + 17,2 x 72) + 0,8 x (47 x 120 + 28,2 x 110 + 18,8 x 88)
                    = 0,5 x 7860,4 + 0,8 x 10396,4 = 3930,2 + 8317,12 = 12247,32.
  A_2027 = 1,1 x (0,95 / 0,90) x 12247,32 = 21330749 / 1500.
  cotisants : (0,95 / 0,90) x (0,5 x 86 + 0,8 x 94) = (0,95 / 0,90) x 118,2 = 3743 / 30.
  Classe 2+ de 2027 : F (58 ; 39,4 ; 16,6), H (25,65 ; 36,45 ; 25,65). Convention D21 : la classe ouverte est
  rattachée à la génération t - A, donc entièrement « nouveaux liquidants » en 2027, avec la pension
  lambda x kappa x m1 moyen des liquidants (F 8, H 9) x G.
  B_2027 = 1,1 x (24/35) x (8 x (58 + 2 x 39,4 + 0,5 x 16,6) + 9 x (25,65 + 2 x 36,45 + 0,5 x 25,65))
         = 1,1 x (24/35) x (8 x 145,1 + 9 x 111,375) = 407913 / 250.
  C_2027 = tau0 x A_2027 ; D_2027 = B_2027 - C_2027.
Réserve (k = 0,5, r = 2 %) : R_2026 = 0,5 x 1200 = 600 ; R_2027 = 600 x 1,02 - 0 = 612 ;
  R_2028 = 612 x 1,02 - D_2027.
"""
import numpy as np
import pytest

from actuarial_model.model import build_inputs, run_finance
from helpers import toy_finance_setup

TOL = 1e-9
A_2026 = 11392.0
LAMBDA = 24.0 / 35.0
TAU0 = 75.0 / 712.0
A_2027 = 21330749.0 / 1500.0
B_2027 = 407913.0 / 250.0
D_2027 = 47599387.0 / 356000.0
R_2028 = 174630053.0 / 356000.0


@pytest.fixture(scope="module")
def toy(cfg):
    toy_cfg, states, data, paths = toy_finance_setup(cfg)
    inp = build_inputs(toy_cfg, states, data)
    res = run_finance(toy_cfg, inp, paths, k=cfg["toy_finance"]["initial_reserve_k"])
    return toy_cfg, inp, res


def test_toy_population_de_2027_vient_de_la_phase_2(toy):
    _, inp, _ = toy
    # âge 1 et classe 2+ de 2027, par catégorie (calcul à la main de test_toy_example)
    assert inp.n[1, :, 0, 0] == pytest.approx([43.0, 25.8, 17.2], abs=TOL)
    assert inp.n[1, :, 1, 1] == pytest.approx([25.65, 36.45, 25.65], abs=TOL)


def test_toy_lambda_et_tau0(toy):
    _, inp, res = toy
    assert inp.diagnostics["lambda"]["expenditure_before"] == pytest.approx(1750.0, abs=TOL)
    assert inp.diagnostics["lambda"]["reference_total"] == pytest.approx(1200.0, abs=TOL)
    assert inp.diagnostics["lambda"]["lambda"] == pytest.approx(LAMBDA, abs=TOL)
    assert res.tau0 == pytest.approx(TAU0, abs=TOL)


def test_toy_cotisants_et_retraites(toy):
    _, _, res = toy
    assert res.contributors[0, 0] == pytest.approx(112.0, abs=TOL)
    assert res.contributors[0, 1] == pytest.approx(3743.0 / 30.0, abs=TOL)
    assert res.retirees == pytest.approx([110.0, 807.0 / 4.0], abs=TOL)


def test_toy_assiette(toy):
    _, _, res = toy
    assert res.assiette[0, 0] == pytest.approx(A_2026, abs=TOL)
    assert res.assiette[0, 1] == pytest.approx(A_2027, abs=TOL)


def test_toy_prestations_cotisations_deficit(toy):
    _, _, res = toy
    assert res.benefits[0, 0] == pytest.approx(1200.0, abs=TOL)
    assert res.benefits[0, 1] == pytest.approx(B_2027, abs=TOL)
    assert res.contributions[0, 0] == pytest.approx(1200.0, abs=TOL)
    assert res.contributions[0, 1] == pytest.approx(TAU0 * A_2027, abs=TOL)
    assert res.deficit[0, 0] == pytest.approx(0.0, abs=TOL)           # D_2026 = 0 par construction
    assert res.deficit[0, 1] == pytest.approx(D_2027, abs=TOL)


def test_toy_reserve(toy):
    _, _, res = toy
    assert res.reserve[0] == pytest.approx([600.0, 612.0, R_2028], abs=TOL)
    # identité du bilan sur toute la trajectoire
    r = 0.02
    assert res.reserve[0, 1:] == pytest.approx(res.reserve[0, :-1] * (1 + r) - res.deficit[0], abs=TOL)
