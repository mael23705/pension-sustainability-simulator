"""T8 : part de retraités rho (version vectorisée) et rho_bar (D16)."""
import numpy as np
import pytest

from actuarial_model.retirement import (legal_age_array, retired_grid, retired_share, retirement_age_grid,
                                         rho_bar)

YEARS = np.arange(2026, 2066)
AGES = np.arange(20, 101)
DELTA = np.array([[1, 1], [0, 0], [0, 0]])          # valeurs de test, pas des résultats


def test_rho_vaut_zero_ou_un(cfg):
    rho = retired_grid(YEARS, AGES, cfg, DELTA)
    assert rho.shape == (40, 3, 2, 81)
    assert set(np.unique(rho)) <= {0.0, 1.0}


def test_rho_ne_decroit_jamais_avec_l_age_a_generation_fixee(cfg):
    """Pour une génération donnée, dès que rho vaut 1 il reste à 1 aux âges suivants (T8)."""
    rho = retired_grid(YEARS, AGES, cfg, DELTA)
    # une génération g est suivie de t à t+1 en passant de l'âge a à a+1
    for g in (1950, 1960, 1964, 1970, 1990, 2000):
        path = []
        for i, t in enumerate(YEARS):
            a = t - g
            if AGES[0] <= a <= AGES[-1] - 1:      # hors classe ouverte (génération non suivie)
                path.append(rho[i, :, :, a - AGES[0]])
        if path:
            assert np.all(np.diff(np.stack(path), axis=0) >= 0)


def test_coherent_avec_la_fonction_scalaire(cfg):
    rho = retired_grid(YEARS, AGES, cfg, DELTA)
    rng = np.random.default_rng(0)
    for _ in range(300):
        i, k = rng.integers(0, len(YEARS)), rng.integers(0, len(AGES))
        c, s = rng.integers(0, 3), rng.integers(0, 2)
        expected = retired_share(int(AGES[k]), int(YEARS[i] - AGES[k]), cfg, int(DELTA[c, s]))
        assert rho[i, c, s, k] == expected


def test_age_legal_vectorise_egal_au_scalaire(cfg):
    gens = np.array([[1955, 1960, 1961], [1964, 1967, 2000]])
    out = legal_age_array(gens, cfg)
    assert out.tolist() == [[62, 62, 62], [63, 64, 64]]      # tableau 1.4 du COR, arrondi D5


def test_age_de_depart_decale_de_delta(cfg):
    a0 = retirement_age_grid(YEARS, AGES, cfg, np.zeros((3, 2), dtype=int))
    a1 = retirement_age_grid(YEARS, AGES, cfg, np.ones((3, 2), dtype=int))
    assert np.array_equal(a1, a0 + 1)


def test_rho_bar_entre_zero_et_un_et_pondere_par_les_effectifs(cfg):
    rho = retired_grid(YEARS, AGES, cfg, DELTA)
    n = np.ones(rho.shape) * np.array([0.7, 0.19, 0.11])[None, :, None, None]
    rb = rho_bar(n, rho)
    assert rb.shape == (40, 2, 81)
    assert rb.min() >= 0.0 and rb.max() <= 1.0
    # avec ces effectifs, les valeurs possibles sont les sommes de pi_c des catégories retraitées
    assert set(np.round(np.unique(rb), 10)) <= {0.0, 0.11, 0.19, 0.30, 0.70, 0.81, 0.89, 1.0}
    # les effectifs présents comptent, pas les parts initiales : on double le privé
    n2 = n.copy()
    n2[:, 0] *= 2
    assert not np.allclose(rho_bar(n2, rho), rb)


def test_rho_bar_cellule_sans_effectif_vaut_un(cfg):
    rho = retired_grid(YEARS, AGES, cfg, DELTA)
    n = np.zeros(rho.shape)
    assert np.all(rho_bar(n, rho) == 1.0)


def test_classe_ouverte_toujours_retraitee(cfg):
    rho = retired_grid(YEARS, AGES, cfg, DELTA)
    assert np.all(rho[:, :, :, -1] == 1.0)
