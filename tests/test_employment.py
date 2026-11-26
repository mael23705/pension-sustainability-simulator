"""T11 : taux d'emploi conditionnel e = e_obs / (1 - rho_bar) dans [0, 1] ; D6 ; D16 ; D18b."""
import numpy as np
import pytest

from economics import employment as emp


def test_cas_rho_bar_nul():
    e_obs = np.array([0.5, 0.8])
    assert emp.conditional_employment(e_obs, np.zeros(2)) == pytest.approx(e_obs, abs=1e-12)


def test_cas_rho_bar_intermediaire():
    # e = e_obs / (1 - rho_bar) : 0,3 / 0,7 puis 0,2 / 0,5
    out = emp.conditional_employment(np.array([0.3, 0.1]), np.array([0.3, 0.8]))
    assert out == pytest.approx([0.3 / 0.7, 0.1 / 0.2], abs=1e-12)


def test_cas_rho_bar_egal_un_donne_zero_et_pas_une_erreur():
    out = emp.conditional_employment(np.array([0.2, 0.05]), np.array([1.0, 1.0]))
    assert np.all(out == 0.0)


def test_e_superieur_a_un_est_une_erreur_jamais_un_plafond():
    # 0,3 / (1 - 0,8) = 1,5
    with pytest.raises(emp.EmploymentError, match="hors de"):
        emp.conditional_employment(np.array([0.3]), np.array([0.8]))


def test_taux_observe_hors_de_zero_un_est_une_erreur():
    with pytest.raises(emp.EmploymentError):
        emp.conditional_employment(np.array([1.2]), np.array([0.0]))
    with pytest.raises(emp.EmploymentError):
        emp.conditional_employment(np.array([-0.1]), np.array([0.0]))


def test_rho_bar_hors_de_zero_un_est_une_erreur():
    with pytest.raises(emp.EmploymentError):
        emp.conditional_employment(np.array([0.1]), np.array([1.2]))


def test_somme_des_cotisants_egale_emploi_observe():
    """Avec e^R = 0 : somme_c N_c (1 - rho_c) e = N e_obs quand rho_bar < 1."""
    rng = np.random.default_rng(1)
    n = rng.uniform(50, 150, size=(3, 40))                    # effectifs par catégorie et par cellule
    rho = (rng.uniform(size=(3, 40)) < 0.4).astype(float)
    rho[:, 0] = 1.0                                           # une cellule entièrement retraitée
    rb = (n * rho).sum(axis=0) / n.sum(axis=0)
    e_obs = rng.uniform(0.0, 1.0, size=40) * (1.0 - rb)       # e_obs <= 1 - rho_bar : e reste dans [0, 1]
    e = emp.conditional_employment(e_obs, rb)
    contributors = (n * (1 - rho) * e).sum(axis=0)
    ok = rb < 1
    assert contributors[ok] == pytest.approx((n.sum(axis=0) * e_obs)[ok], abs=1e-9)
    assert contributors[~ok] == pytest.approx(0.0, abs=1e-12)


def test_perte_d_emploi_somme_les_cellules_entierement_retraitees():
    n = np.array([100.0, 200.0, 300.0])
    e_obs = np.array([0.5, 0.1, 0.2])
    rb = np.array([0.0, 1.0, 1.0])
    loss, covered = emp.employment_loss(n, e_obs, rb)
    assert loss == pytest.approx(200 * 0.1 + 300 * 0.2, abs=1e-12)
    assert covered == pytest.approx(50 + 20 + 60, abs=1e-12)


def test_facteur_d_echelle_ramene_le_total_a_la_cible():
    survey, target = 29_382_331.0, 30_600_000.0
    f = emp.scale_factor(survey, target)
    assert f * survey == pytest.approx(target, abs=1e-9)
    with pytest.raises(emp.EmploymentError):
        emp.scale_factor(0.0, target)


def test_mise_a_l_echelle_au_dela_de_un_est_une_erreur():
    with pytest.raises(emp.EmploymentError):
        emp.scale_to_national_accounts(np.array([0.97]), 1.05)


def test_chomage_d18b():
    out = emp.unemployment_adjusted(np.array([0.5, 0.8]), u_t=0.10, u_ref=0.08)
    assert out == pytest.approx(np.array([0.5, 0.8]) * 0.90 / 0.92, abs=1e-12)
    with pytest.raises(emp.EmploymentError):          # 0,98 x 0,95 / 0,5 > 1
        emp.unemployment_adjusted(np.array([0.98]), u_t=0.05, u_ref=0.5)
    with pytest.raises(emp.EmploymentError):
        emp.unemployment_factor(np.array([1.0]), 0.08)


def test_profil_reel_dans_zero_un(cfg):
    from pathlib import Path
    path = Path(__file__).resolve().parent.parent / "data" / "processed" / "taux-emploi-age-sexe-2025.csv"
    if not path.exists():
        pytest.skip("Table d'emploi absente de data/processed/ (reconstruite par build_employment_table.py).")
    prof = emp.load_employment_profile(path, 100)
    emp.check_rates(prof.e_obs, "profil")
    assert prof.e_obs[:, :15].sum() == 0.0                       # aucun emploi avant 15 ans
    assert prof.survey_employment == pytest.approx(29.38e6, rel=0.002)
    # points de la fiche 6 : taux à 62, 63 et 64 ans (F puis H), à 0,3 point près
    assert prof.e_obs[0, 62:65] == pytest.approx([0.440, 0.274, 0.211], abs=0.003)
    assert prof.e_obs[1, 62:65] == pytest.approx([0.432, 0.304, 0.238], abs=0.003)
