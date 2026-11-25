"""Test 2 : reproduction de la projection Insee 2026, scénario central (cahier 7.3).

Le moteur est alimenté avec les mêmes hypothèses que la projection (mortalité, fécondité,
migrations) et la même population de départ ; on compare CHAQUE année :
- population totale : erreur relative <= 1 % ;
- 0-19, 20-59, 60 ans et plus : erreur relative <= 2 %.
Les seuils viennent du YAML. Un dépassement fait échouer le test : on ne l'assouplit pas
sans justification écrite dans docs/plan-de-validation.md (section 8).
Ce test lit data/raw/ : ignoré si les fichiers sont absents (GitHub Actions).
"""
from pathlib import Path

import numpy as np
import pytest

from config import affiliation_shares, get_param, raw_data_path
from data_io.insee import aggregate_open_class, load_central_projection, load_population_2026, year_params
from demography.comparison import age_group_totals, relative_errors, run_projection
from demography.population import initial_population

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def projection_run(cfg):
    pop_path = raw_data_path(cfg, ROOT, "insee_population_file")
    proj_path = raw_data_path(cfg, ROOT, "insee_projection_file")
    if not (pop_path.exists() and proj_path.exists()):
        pytest.skip("Fichiers Insee absents de data/raw/ (ignorés par Git).")
    A = get_param(cfg, "demography.open_class_age")
    a0 = get_param(cfg, "demography.entry_age_a0")
    pi = affiliation_shares(cfg)
    first = get_param(cfg, "horizon.start_year")
    n_steps = get_param(cfg, "horizon.flow_years")
    include_adj = get_param(cfg, "demography.insee_adjustment_included")
    policy = get_param(cfg, "demography.migration_overflow_policy")

    n_init = load_population_2026(
        pop_path, sheet=get_param(cfg, "data_files.insee_population_sheet"),
        champ=get_param(cfg, "data_files.insee_population_scope"))
    proj = load_central_projection(proj_path)
    state0 = initial_population(aggregate_open_class(n_init, A), a0, pi)

    states, results = run_projection(
        state0, lambda t, _s: year_params(proj, t, A, include_adjustment=include_adj),
        first, n_steps, pi, pi, policy)
    return cfg, proj, states, results, first


def _errors(cfg, proj, states, first):
    groups = get_param(cfg, "tests.insee_age_groups")
    err_total, err_groups = [], []
    for k, st in enumerate(states):
        ref = proj.population[:, :, proj.year_index(first + k)].sum(axis=0)   # (106,)
        err_total.append(relative_errors(st.total(), ref.sum()))
        err_groups.append(relative_errors(age_group_totals(st.by_age().sum(axis=0), groups),
                                          age_group_totals(ref, groups)))
    return np.array(err_total), np.array(err_groups)


def test_population_totale_dans_le_seuil_chaque_annee(projection_run):
    cfg, proj, states, _, first = projection_run
    err_total, _ = _errors(cfg, proj, states, first)
    limit = get_param(cfg, "tests.insee_total_population_max_relative_error")
    assert np.abs(err_total).max() <= limit, f"max = {np.abs(err_total).max():.4%}"


def test_groupes_d_age_dans_le_seuil_chaque_annee(projection_run):
    cfg, proj, states, _, first = projection_run
    _, err_groups = _errors(cfg, proj, states, first)
    limit = get_param(cfg, "tests.insee_age_group_max_relative_error")
    assert np.abs(err_groups).max() <= limit, f"max = {np.abs(err_groups).max(axis=0)}"


def test_aucune_alerte_et_aucun_effectif_negatif(projection_run):
    _, _, states, results, _ = projection_run
    assert all(r.alerts == [] for r in results)
    assert min(min(s.n.min(), s.n_pre.min()) for s in states) >= 0


def test_solde_migratoire_du_moteur_egal_a_celui_de_la_source(projection_run):
    """T9 sur les données Insee : somme (solde + ajustement) de chaque année, tous âges."""
    cfg, proj, _, results, first = projection_run
    for k, res in enumerate(results):
        i = proj.year_index(first + k)
        source = proj.net_migration[:, :, i].sum() + proj.adjustment[:, :, i].sum()
        assert res.net_migration_applied == pytest.approx(source, rel=1e-9)


def test_population_par_sexe_dans_le_seuil_chaque_annee(projection_run):
    """Contrôle complémentaire (hors cahier) : chaque sexe, même seuil que la population totale."""
    cfg, proj, states, _, first = projection_run
    limit = get_param(cfg, "tests.insee_total_population_max_relative_error")
    for k, st in enumerate(states):
        ref = proj.population[:, :, proj.year_index(first + k)].sum(axis=1)   # (S,)
        err = relative_errors(st.n_pre.sum(axis=1) + st.n.sum(axis=(0, 2)), ref)
        assert np.abs(err).max() <= limit, f"année {first + k} : {err}"
