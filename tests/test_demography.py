"""Tests démographiques T1 à T10 et T12 (docs/plan-de-validation.md, section 3).

T11 (taux d'emploi) sera ajouté en phase 3. Comparaisons de flottants avec pytest.approx,
tolérance lue dans le YAML (1e-9). Les populations et paramètres aléatoires sont des
valeurs de test (graine fixe issue du YAML), jamais des résultats.
"""
import copy

import numpy as np
import pytest

from actuarial_model.retirement import legal_age, retired_share
from config import ConfigError, affiliation_shares, conservation_tolerance, get_param
from conventions import SEX_F
from demography.engine import STEP_ORDER, age_population, apply_mortality, step_year
from demography.migration import MigrationOverflowError, split_gross_flows
from demography.population import PopulationState, YearParams, initial_population
from helpers import random_state_and_params, toy_params, toy_pi, toy_state


@pytest.fixture()
def rng(cfg):
    return np.random.default_rng(get_param(cfg, "simulation.random_seed"))


def _zero_flows(params: YearParams) -> YearParams:
    """Mêmes paramètres, sans décès, naissances ni migrations."""
    q_age = np.where(np.isnan(params.q_age), np.nan, 0.0)
    return YearParams(
        q_birth=np.zeros_like(params.q_birth), q_age=q_age, q_open=np.zeros_like(params.q_open),
        fertility=np.zeros_like(params.fertility), girl_share=params.girl_share,
        net_migration=np.zeros_like(params.net_migration),
    )


# --- T1 : conservation des effectifs ---------------------------------------------------
def test_T1_sans_flux_la_population_est_conservee(cfg, rng):
    tol = conservation_tolerance(cfg)
    state, params, pi = random_state_and_params(rng)
    res = step_year(state, _zero_flows(params), pi, pi, 2026)
    assert res.state.total() == pytest.approx(state.total(), abs=tol)


def test_T1_bilan_population_naissances_deces_migrations(cfg, rng):
    """N(t+1) = N(t) + naissances - décès + solde migratoire (avec décès des nouveau-nés)."""
    tol = conservation_tolerance(cfg)
    for _ in range(20):
        state, params, pi = random_state_and_params(rng)
        res = step_year(state, params, pi, pi, 2026, overflow_policy="log_only")
        expected = state.total() + res.births - res.deaths + res.net_migration_applied
        assert res.state.total() == pytest.approx(expected, rel=tol)


# --- T2 : aucun effectif négatif -------------------------------------------------------
def test_T2_effectifs_positifs_sur_le_cas_jouet(cfg):
    state = toy_state(cfg)
    for year in (2026, 2027):
        state = step_year(state, toy_params(cfg, year), toy_pi(cfg), toy_pi(cfg), year).state
        assert state.n.min() >= 0 and state.n_pre.min() >= 0


# --- T3 : cohérence des transitions par âge, sexe et catégorie --------------------------
def test_T3_chaque_classe_vient_de_la_classe_precedente(cfg, rng):
    state, params, pi = random_state_and_params(rng)
    new = step_year(state, _zero_flows(params), pi, pi, 2026).state
    a0, A = state.a0, state.open_age
    # âges sous a0 : décalage d'un an (la classe 0 est vide : pas de naissances ici)
    assert new.n_pre[:, 1:] == pytest.approx(state.n_pre[:, :-1])
    assert new.n_pre[:, 0] == pytest.approx(0.0)
    # âges a0+1 .. A-1 : décalage par catégorie
    assert new.n[:, :, 1:-1] == pytest.approx(state.n[:, :, :-2])


# --- T4 : attribution des catégories à a0 ------------------------------------------------
def test_T4_somme_des_categories_a_a0(cfg, rng):
    tol = conservation_tolerance(cfg)
    state, params, pi = random_state_and_params(rng)
    new = step_year(state, _zero_flows(params), pi, pi, 2026).state
    assert new.n[:, :, 0].sum(axis=0) == pytest.approx(state.n_pre[:, -1], abs=tol)
    assert new.n[:, :, 0] == pytest.approx(pi[:, None] * state.n_pre[:, -1][None, :], abs=tol)


def test_T4_population_initiale_repartie_selon_pi(cfg, rng):
    tol = conservation_tolerance(cfg)
    by_age = rng.uniform(100, 200, size=(2, 11))
    pi = affiliation_shares(cfg)
    state = initial_population(by_age, a0=4, pi=pi)
    assert state.by_age() == pytest.approx(by_age, abs=tol)
    assert state.n[:, 0, 0] == pytest.approx(pi * by_age[0, 4], abs=tol)


# --- T5 : conservation de la somme des catégories -----------------------------------------
def test_T5_somme_des_categories_egale_au_modele_sans_categorie(cfg, rng):
    """Trois catégories ou une seule : mêmes effectifs par sexe et âge, 6 années de suite."""
    tol = conservation_tolerance(cfg)
    state3, params, pi = random_state_and_params(rng)
    by_age = state3.by_age()
    state1 = PopulationState(state3.n_pre.copy(), by_age[None, :, state3.a0 :].copy())
    one = np.array([1.0])
    for k in range(6):
        state3 = step_year(state3, params, pi, pi, 2026 + k, "log_only").state
        state1 = step_year(state1, params, one, one, 2026 + k, "log_only").state
        assert state3.by_age() == pytest.approx(state1.by_age(), rel=tol)


# --- T6 : ordre du calendrier annuel --------------------------------------------------------
def test_T6_ordre_du_calendrier(cfg, rng):
    state, params, pi = random_state_and_params(rng)
    for k in range(5):
        res = step_year(state, params, pi, pi, 2026 + k, "log_only")
        assert res.trace == list(STEP_ORDER) == ["mortalite", "vieillissement", "migrations", "naissances"]
        state = res.state


# --- T7 : classe ouverte -----------------------------------------------------------------------
def test_T7_classe_ouverte_recoit_les_survivants_de_A_moins_1_et_de_A(cfg, rng):
    tol = conservation_tolerance(cfg)
    state, params, pi = random_state_and_params(rng)
    A = state.open_age
    survivors, _ = apply_mortality(state, params)
    aged = age_population(survivors, pi)
    by_age = state.by_age()
    expected = (by_age[:, A - 1] * (1 - params.q_age[:, A]) + by_age[:, A] * (1 - params.q_open))
    assert aged.by_age()[:, A] == pytest.approx(expected, abs=tol)


def test_T7_sans_mortalite_la_classe_ouverte_est_la_somme_des_deux(cfg, rng):
    tol = conservation_tolerance(cfg)
    state, params, pi = random_state_and_params(rng)
    new = step_year(state, _zero_flows(params), pi, pi, 2026).state
    A = state.open_age
    assert new.by_age()[:, A] == pytest.approx(
        state.by_age()[:, A - 1] + state.by_age()[:, A], abs=tol)


# --- T8 : part de retraités rho -----------------------------------------------------------------
def test_T8_rho_vaut_0_ou_1_et_ne_decroit_pas_avec_l_age(cfg):
    low, high = get_param(cfg, "retirement.delta_effective_minus_legal.test_range_years")
    for generation in range(1950, 2001):
        for delta in range(low, high + 1):
            rho = [retired_share(a, generation, cfg, delta) for a in range(0, 111)]
            assert set(rho) <= {0.0, 1.0}
            assert all(b >= a for a, b in zip(rho, rho[1:]))
            assert rho[0] == 0.0 and rho[-1] == 1.0


def test_T8_ages_legaux_du_tableau_cor(cfg):
    assert legal_age(1960, cfg) == 62
    assert legal_age(1969, cfg) == 64
    assert legal_age(1950, cfg) == get_param(cfg, "retirement.legal_age_by_generation.earlier_generations")
    assert legal_age(1985, cfg) == get_param(cfg, "retirement.legal_age_by_generation.later_generations")


# --- T9 : migrations, solde total ----------------------------------------------------------------------
def test_T9_solde_du_moteur_egal_a_celui_de_la_source(cfg, rng):
    tol = conservation_tolerance(cfg)
    state, params, pi = random_state_and_params(rng)
    # Sans décès ni naissances : la variation d'effectif est exactement le solde migratoire.
    flows_only = YearParams(
        q_birth=np.zeros(2), q_age=np.where(np.isnan(params.q_age), np.nan, 0.0),
        q_open=np.zeros(2), fertility=np.zeros_like(params.fertility), girl_share=params.girl_share,
        net_migration=params.net_migration,
    )
    res = step_year(state, flows_only, pi, pi, 2026, "log_only")
    source = params.net_migration.sum()
    assert res.net_migration_applied == pytest.approx(source, abs=tol)
    assert res.state.total() - state.total() == pytest.approx(source, abs=tol)


def test_T9_flux_bruts_preservent_le_solde():
    net = np.array([[3.0, -2.0, 0.0], [-1.5, 4.0, -0.5]])
    m_plus, m_minus = split_gross_flows(net)
    assert (m_plus >= 0).all() and (m_minus >= 0).all()
    assert m_plus - m_minus == pytest.approx(net, abs=0)
    assert not ((m_plus > 0) & (m_minus > 0)).any()


# --- T10 : migrations, départs ----------------------------------------------------------------------------
def _toy_with_net_migration(cfg, age: int, sex: int, value: float):
    params = toy_params(cfg, 2026)
    net = np.zeros_like(params.net_migration)
    net[sex, age] = value
    return YearParams(params.q_birth, params.q_age, params.q_open, params.fertility,
                      params.girl_share, net)


def test_T10_depassement_leve_une_erreur_explicite(cfg):
    params = _toy_with_net_migration(cfg, age=1, sex=SEX_F, value=-1000.0)
    with pytest.raises(MigrationOverflowError, match="supérieurs à l'effectif présent"):
        step_year(toy_state(cfg), params, toy_pi(cfg), toy_pi(cfg), 2026)


def test_T10_depassement_journalise_jamais_tronque(cfg):
    """En politique log_only, l'alerte est dans le journal et l'effectif n'est pas rabaissé à 0."""
    params = _toy_with_net_migration(cfg, age=1, sex=SEX_F, value=-1000.0)
    res = step_year(toy_state(cfg), params, toy_pi(cfg), toy_pi(cfg), 2026, overflow_policy="log_only")
    assert [a.code for a in res.alerts] == ["migration_overflow"]
    assert res.alerts[0].details["departures"] == 1000.0
    assert res.state.n[:, SEX_F, 0].sum() < 0   # le dépassement reste visible (T2 le détecte)


def test_T10_age_zero_depassement_signale(cfg):
    params = _toy_with_net_migration(cfg, age=0, sex=SEX_F, value=-1000.0)
    with pytest.raises(MigrationOverflowError):
        step_year(toy_state(cfg), params, toy_pi(cfg), toy_pi(cfg), 2026)


def test_T10_sans_depassement_aucun_effectif_negatif(cfg, rng):
    for _ in range(30):
        state, params, pi = random_state_and_params(rng)
        # départs au plus égaux à 1 : bien inférieurs aux effectifs présents (>= 50 x 0.7)
        net = np.clip(params.net_migration, -1.0, None)
        p = YearParams(params.q_birth, params.q_age, params.q_open, params.fertility,
                       params.girl_share, net)
        res = step_year(state, p, pi, pi, 2026)
        assert res.alerts == []
        assert res.state.n.min() >= 0 and res.state.n_pre.min() >= 0


# --- T12 : parts pi_c ----------------------------------------------------------------------------------------
def test_T12_parts_somment_a_un_et_sont_dans_les_plages(cfg):
    pi = affiliation_shares(cfg)
    assert pi.sum() == pytest.approx(1.0, abs=conservation_tolerance(cfg))
    assert dict(zip(cfg["demography"]["categories"], pi)) == cfg["demography"]["affiliation_shares_pi"]["values"]


def test_T12_une_part_hors_plage_est_refusee(cfg):
    bad = copy.deepcopy(cfg)
    bad["demography"]["affiliation_shares_pi"]["values"].update(
        {"prive": 0.60, "public": 0.29, "independants": 0.11})   # public hors de [0.17, 0.21]
    with pytest.raises(ConfigError, match="hors de la plage"):
        affiliation_shares(bad)


def test_T12_somme_differente_de_un_est_refusee(cfg):
    bad = copy.deepcopy(cfg)
    bad["demography"]["affiliation_shares_pi"]["values"]["prive"] = 0.75
    with pytest.raises(ConfigError, match="sommer à 1"):
        affiliation_shares(bad)
