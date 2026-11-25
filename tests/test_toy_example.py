"""Test 1 : validation mécanique sur le cas jouet, calculé à la main (plan de validation, section 4).

Les paramètres sont dans config/assumptions.yaml (bloc `toy_example`, statut toy_example).
Les valeurs attendues ci-dessous ont été calculées sur papier, dans l'ordre du calendrier :
mortalité -> vieillissement -> migrations -> naissances. Elles ne servent jamais à un résultat.

Notation : F = femmes, M = hommes ; âges 0, 1 et 2+ (classe ouverte) ; catégories
(privé, public, indépendants) avec pi = (0.5, 0.3, 0.2) ; a0 = 1.
Survie : F : 0.9 (0->1), 0.8 (1->2), 0.7 (2+) ; M : 0.8, 0.75, 0.6 ; nouveau-nés : F 0.9, M 0.8.

=== Année 2026 -> 2027 ===
Population au 1er janvier 2026 : F = [100 | 50 20 10 | 20 30 10], M = [110 | 30 30 30 | 10 30 10]
(âge 0 | âge 1 par catégorie | âge 2+ par catégorie).
Naissances : 0.5 x F(âge 1) + 0.25 x F(âge 2+) = 0.5 x 80 + 0.25 x 60 = 55 ; 27.5 filles, 27.5 garçons.
Survivants des nouveau-nés : F 27.5 x 0.9 = 24.75 ; M 27.5 x 0.8 = 22.
Mortalité puis vieillissement, femmes :
  entrée à l'âge 1 : 100 x 0.9 = 90 -> (45, 27, 18)
  âge 2+ : (50, 20, 10) x 0.8 + (20, 30, 10) x 0.7 = (40, 16, 8) + (14, 21, 7) = (54, 37, 15)
hommes :
  entrée à l'âge 1 : 110 x 0.8 = 88 -> (44, 26.4, 17.6)
  âge 2+ : (30, 30, 30) x 0.75 + (10, 30, 10) x 0.6 = (22.5, 22.5, 22.5) + (6, 18, 6) = (28.5, 40.5, 28.5)
Migrations (solde) : F = (+10, -4, +8) ; M = (-5, +6, -9.75) aux âges (0, 1, 2+)
  F âge 1 : départs 4 au prorata de (45, 27, 18) -> x (1 - 4/90) -> (43, 25.8, 17.2)
  F âge 2+ : arrivées 8 selon pi -> (54 + 4, 37 + 2.4, 15 + 1.6) = (58, 39.4, 16.6)
  M âge 1 : arrivées 6 selon pi -> (44 + 3, 26.4 + 1.8, 17.6 + 1.2) = (47, 28.2, 18.8)
  M âge 2+ : départs 9.75 sur 97.5 (10 %) -> (25.65, 36.45, 25.65)
Naissances (avec le solde de l'âge 0) : F 24.75 + 10 = 34.75 ; M 22 - 5 = 17.
Population au 1er janvier 2027 :
  F = [34.75 | 43 25.8 17.2 | 58 39.4 16.6]   M = [17 | 47 28.2 18.8 | 25.65 36.45 25.65]

=== Année 2027 -> 2028 ===
Naissances : 0.5 x 86 + 0.25 x 114 = 71.5 ; 35.75 filles, 35.75 garçons ; survivants F 32.175, M 28.6.
Femmes : entrée à l'âge 1 : 34.75 x 0.9 = 31.275 -> (15.6375, 9.3825, 6.255)
  âge 2+ : (43, 25.8, 17.2) x 0.8 + (58, 39.4, 16.6) x 0.7 = (34.4, 20.64, 13.76) + (40.6, 27.58, 11.62)
         = (75, 48.22, 25.38) ; départs 14.86 sur 148.6 (10 %) -> (67.5, 43.398, 22.842)
  âge 0 : 32.175 - 10 = 22.175
Hommes : entrée à l'âge 1 : 17 x 0.8 = 13.6 -> (6.8, 4.08, 2.72)
  âge 2+ : (47, 28.2, 18.8) x 0.75 + (25.65, 36.45, 25.65) x 0.6 = (35.25, 21.15, 14.1) + (15.39, 21.87, 15.39)
         = (50.64, 43.02, 29.49) ; aucun solde aux âges 1 et 2+
  âge 0 : 28.6 + 3 = 31.6
Population au 1er janvier 2028 :
  F = [22.175 | 15.6375 9.3825 6.255 | 67.5 43.398 22.842]   M = [31.6 | 6.8 4.08 2.72 | 50.64 43.02 29.49]
"""
import numpy as np
import pytest

from config import conservation_tolerance
from conventions import SEX_F, SEX_M
from demography.engine import STEP_ORDER, step_year
from demography.population import PopulationState
from helpers import toy_params, toy_pi, toy_state

# Valeurs attendues, calculées à la main (voir en-tête).
EXPECTED_2027 = {
    "pre": np.array([[34.75], [17.0]]),
    "n": np.array([  # [catégorie][sexe][âge 1, âge 2+]
        [[43.0, 58.0], [47.0, 25.65]],
        [[25.8, 39.4], [28.2, 36.45]],
        [[17.2, 16.6], [18.8, 25.65]],
    ]),
}
EXPECTED_2028 = {
    "pre": np.array([[22.175], [31.6]]),
    "n": np.array([
        [[15.6375, 67.5], [6.8, 50.64]],
        [[9.3825, 43.398], [4.08, 43.02]],
        [[6.255, 22.842], [2.72, 29.49]],
    ]),
}


def run_two_years(cfg, pi, pi_mig):
    state = toy_state(cfg)
    r1 = step_year(state, toy_params(cfg, 2026), pi, pi_mig, 2026)
    r2 = step_year(r1.state, toy_params(cfg, 2027), pi, pi_mig, 2027)
    return r1, r2


def test_toy_trois_categories_reproduit_la_main(cfg):
    tol = conservation_tolerance(cfg)
    pi = toy_pi(cfg)
    r1, r2 = run_two_years(cfg, pi, pi)
    assert r1.state.n_pre == pytest.approx(EXPECTED_2027["pre"], abs=tol)
    assert r1.state.n == pytest.approx(EXPECTED_2027["n"], abs=tol)
    assert r2.state.n_pre == pytest.approx(EXPECTED_2028["pre"], abs=tol)
    assert r2.state.n == pytest.approx(EXPECTED_2028["n"], abs=tol)


def test_toy_flux_de_la_premiere_annee(cfg):
    tol = conservation_tolerance(cfg)
    r1, r2 = run_two_years(cfg, toy_pi(cfg), toy_pi(cfg))
    assert r1.births == pytest.approx(55.0, abs=tol)
    assert r2.births == pytest.approx(71.5, abs=tol)
    # Soldes migratoires : F (10 - 4 + 8) + M (-5 + 6 - 9.75) = 14 - 8.75 ; puis -24.86 + 3
    assert r1.net_migration_applied == pytest.approx(14.0 - 8.75, abs=tol)
    assert r2.net_migration_applied == pytest.approx(-24.86 + 3.0, abs=tol)
    assert r1.trace == list(STEP_ORDER)
    assert r1.alerts == [] and r2.alerts == []


def test_toy_une_seule_categorie_meme_totaux(cfg):
    """Une seule catégorie (pi = 1) : mêmes effectifs par âge et par sexe."""
    tol = conservation_tolerance(cfg)
    one = np.array([1.0])
    three = toy_state(cfg)
    by_age = three.by_age()
    state1 = PopulationState(three.n_pre.copy(), by_age[None, :, three.a0 :].copy())
    r1 = step_year(state1, toy_params(cfg, 2026), one, one, 2026)
    r2 = step_year(r1.state, toy_params(cfg, 2027), one, one, 2027)
    expected_by_age_2027 = np.array([[34.75, 86.0, 114.0], [17.0, 94.0, 87.75]])
    expected_by_age_2028 = np.array([[22.175, 31.275, 133.74], [31.6, 13.6, 123.15]])
    assert r1.state.by_age() == pytest.approx(expected_by_age_2027, abs=tol)
    assert r2.state.by_age() == pytest.approx(expected_by_age_2028, abs=tol)
    assert r2.state.by_age()[SEX_F].sum() == pytest.approx(187.19, abs=tol)
    assert r2.state.by_age()[SEX_M].sum() == pytest.approx(168.35, abs=tol)


def test_toy_repartition_filles_garcons_a_la_naissance(cfg):
    """Part de filles différente de 0,5 : 55 naissances, 25 % de filles (calcul à la main).

    Filles : 55 x 0.25 = 13.75 ; survivantes 13.75 x 0.9 = 12.375 ; + solde 10 = 22.375.
    Garçons : 55 x 0.75 = 41.25 ; survivants 41.25 x 0.8 = 33 ; + solde (-5) = 28.
    """
    from demography.population import YearParams

    tol = conservation_tolerance(cfg)
    p = toy_params(cfg, 2026)
    p = YearParams(p.q_birth, p.q_age, p.q_open, p.fertility, 0.25, p.net_migration)
    res = step_year(toy_state(cfg), p, toy_pi(cfg), toy_pi(cfg), 2026)
    assert res.state.n_pre[SEX_F, 0] == pytest.approx(22.375, abs=tol)
    assert res.state.n_pre[SEX_M, 0] == pytest.approx(28.0, abs=tol)
