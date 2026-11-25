"""Chargement des fichiers Insee et agrégation de la classe ouverte (étape 3 du plan).

Ces tests lisent data/raw/ (non versionné) : ils sont ignorés si les fichiers sont absents,
par exemple dans GitHub Actions.
"""
from pathlib import Path

import numpy as np
import pytest

from config import get_param, raw_data_path
from conventions import SEX_F, SEX_M
from data_io.insee import (
    aggregate_open_class, load_central_projection, load_population_2026, open_class_quotient,
    year_params,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def paths(cfg):
    pop = raw_data_path(cfg, ROOT, "insee_population_file")
    proj = raw_data_path(cfg, ROOT, "insee_projection_file")
    if not (pop.exists() and proj.exists()):
        pytest.skip("Fichiers Insee absents de data/raw/ (ignorés par Git).")
    return pop, proj


@pytest.fixture(scope="module")
def n_init(cfg, paths):
    return load_population_2026(
        paths[0], sheet=get_param(cfg, "data_files.insee_population_sheet"),
        champ=get_param(cfg, "data_files.insee_population_scope"))


@pytest.fixture(scope="module")
def proj(paths):
    return load_central_projection(paths[1])


def test_population_2026_forme_et_somme(n_init):
    assert n_init.shape == (2, 106)
    assert (n_init >= 0).all()
    assert n_init[SEX_F].sum() > n_init[SEX_M].sum()   # plus de femmes que d'hommes


def test_population_2026_identique_dans_les_deux_fichiers(n_init, proj):
    """Vérification de comparabilité n°1 : même population au 1er janvier 2026."""
    ref = proj.population[:, :, proj.year_index(2026)]
    assert n_init == pytest.approx(ref, abs=0.5)


def test_projection_forme_et_annees(proj):
    assert proj.years[0] == 1962 and proj.years[-1] == 2070
    assert proj.mortality.shape[1] == 121 and proj.fertility.shape[0] == 36
    for year in (2026, 2065, 2066):
        i = proj.year_index(year)
        assert np.isfinite(proj.mortality[:, :, i]).all()
        assert np.isfinite(proj.net_migration[:, :, i]).all() or year == 2066


def test_quotients_dans_zero_un(proj):
    i0, i1 = proj.year_index(2026), proj.year_index(2065)
    q = proj.mortality[:, :, i0 : i1 + 1]
    assert (q > 0).all() and (q <= 1).all()


def test_agregation_classe_ouverte(proj):
    """Vérification de comparabilité n°4 : 100-104 + 105+ regroupés en 100+ sans perte."""
    pop = proj.population[:, :, proj.year_index(2026)]
    agg = aggregate_open_class(pop, 100)
    assert agg.shape == (2, 101)
    assert agg.sum() == pytest.approx(pop.sum(), abs=1e-6)
    assert agg[:, 100] == pytest.approx(pop[:, 100:].sum(axis=1), abs=1e-6)
    assert agg[:, :100] == pytest.approx(pop[:, :100])


def test_agregation_classe_ouverte_exemple_simple():
    values = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    assert aggregate_open_class(values, 2) == pytest.approx(np.array([[1.0, 2.0, 12.0]]))
    with pytest.raises(ValueError):
        aggregate_open_class(values, 5)


def test_quotient_classe_ouverte_entre_les_quotients_extremes(proj):
    i = proj.year_index(2026)
    q = proj.mortality[:, :, i]
    qo = open_class_quotient(q, proj.population[:, :, i], 100)
    assert ((qo >= q[:, 101:107].min(axis=1)) & (qo <= q[:, 101:107].max(axis=1))).all()


def test_year_params_valides_pour_tout_l_horizon(cfg, proj):
    A = get_param(cfg, "demography.open_class_age")
    first = get_param(cfg, "horizon.start_year")
    n = get_param(cfg, "horizon.flow_years")
    for t in range(first, first + n):
        year_params(proj, t, A).validate(A)
