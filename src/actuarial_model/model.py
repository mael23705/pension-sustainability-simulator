"""Moteur financier : de la population projetée au bilan annuel (phase 3).

Chaîne : population N[t, c, s, k] (phase 2)  ->  retraités rho  ->  cotisants K (D16)  ->  assiette A_t
         ->  pensions B_t = stock (D17) + nouveaux liquidants (D20)  ->  tau0, C_t, D_t, R_t.

Axes : t = année (T = 40, 2026-2065), c = catégorie, s = sexe, k = âge a0 + k (le dernier = classe ouverte).
Montants en euros constants 2026, annuels. La population est déterministe (phase 3) ; seuls les paramètres
macroéconomiques portent un axe « simulations » : A et B ne dépendent des simulations que par les
facteurs G[sim, t] (salaires réels) et phi[sim, t] (chômage), donc le calcul est vectorisé sans boucle sur sim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from actuarial_model import calibration as cal
from actuarial_model.finance import contributions, deficit, reserves
from actuarial_model.retirement import retired_grid, retirement_age_grid, rho_bar as rho_bar_fn
from config import ConfigError, affiliation_shares, get_param, raw_data_path
from conventions import N_SEXES
from data_io import eacr
from demography.population import PopulationState
from economics import employment as emp
from economics import macro, wages


# ------------------------------------------------------------------------------------ données

@dataclass(frozen=True)
class Phase3Data:
    """Données observées nécessaires à la calibration (tableaux par sexe et âge de 0 à A)."""

    stock_eff: np.ndarray        # (S, A+1)
    stock_m1: np.ndarray         # (S, A+1)
    stock_d13_factor: float
    new_eff: np.ndarray          # (S, A+1)
    new_m1: np.ndarray           # (S, A+1)
    profile: emp.EmploymentProfile


def load_phase3_data(cfg: dict, root: str | Path) -> Phase3Data:
    """Lit les tables dérivées de `data/processed/` (reconstruites par les scripts build_*)."""
    root = Path(root)
    proc = root / get_param(cfg, "data_files.processed_dir")
    A = get_param(cfg, "demography.open_class_age")
    s_eff, s_m1, d13 = eacr.stock_arrays(proc / get_param(cfg, "data_files.eacr_stock_table"), A)
    n_eff, n_m1 = eacr.new_retirees_arrays(proc / get_param(cfg, "data_files.eacr_new_retirees_table"), A)
    prof = emp.load_employment_profile(proc / get_param(cfg, "data_files.employment_table"), A)
    return Phase3Data(s_eff, s_m1, d13, n_eff, n_m1, prof)


def project_population(cfg: dict, root: str | Path) -> list[PopulationState]:
    """Populations au 1er janvier 2026 à 2066 (moteur de la phase 2, scénario central de l'Insee)."""
    from data_io.insee import aggregate_open_class, load_central_projection, load_population_2026, year_params
    from demography.comparison import run_projection
    from demography.population import initial_population

    root = Path(root)
    A = get_param(cfg, "demography.open_class_age")
    a0 = get_param(cfg, "demography.entry_age_a0")
    pi = affiliation_shares(cfg)
    first = get_param(cfg, "horizon.start_year")
    n_init = load_population_2026(raw_data_path(cfg, root, "insee_population_file"),
                                  get_param(cfg, "data_files.insee_population_sheet"),
                                  get_param(cfg, "data_files.insee_population_scope"))
    proj = load_central_projection(raw_data_path(cfg, root, "insee_projection_file"))
    adj = get_param(cfg, "demography.insee_adjustment_included")
    state0 = initial_population(aggregate_open_class(n_init, A), a0, pi)
    states, _ = run_projection(state0, lambda t, _s: year_params(proj, t, A, include_adjustment=adj),
                               first, get_param(cfg, "horizon.flow_years"), pi, pi,
                               get_param(cfg, "demography.migration_overflow_policy"))
    return states


# ------------------------------------------------------------------------------------ entrées du modèle

@dataclass
class ModelInputs:
    """Tout ce qui ne dépend pas des simulations : calculé une fois."""

    years: np.ndarray                 # (T,)
    ages: np.ndarray                  # (K,)
    n: np.ndarray                     # (T, C, S, K) effectifs au 1er janvier
    delta: np.ndarray                 # (C, S) entiers
    rho: np.ndarray                   # (T, C, S, K)
    rho_bar: np.ndarray               # (T, S, K)
    e_base: np.ndarray                # (T, S, K) taux conditionnel au niveau de chômage de 2025 (phi = 1)
    contributors_base: np.ndarray     # (T,) cotisants pour phi = 1
    assiette_base: np.ndarray         # (T,) A_t pour G = 1 et phi = 1, euros 2026
    retirees: np.ndarray              # (T,)
    benefits_stock: np.ndarray        # (T,) pensions du stock de 2026 encore vivant
    new_matrix: np.ndarray            # (T, T) M[tau, t] : pensions de la génération partie en tau, versées en t (G = 1)
    wages: np.ndarray                 # (C, S, K)
    pension_stock: np.ndarray         # (C, S, K) pension annuelle recalée par lambda
    theta: np.ndarray                 # (C, S)
    loss_base: np.ndarray             # (T,) perte d'emploi D16, personnes, phi = 1
    covered_employment_base: np.ndarray   # (T,) emploi observé couvert par le modèle, phi = 1
    diagnostics: dict = field(default_factory=dict)

    @property
    def n_years(self) -> int:
        return len(self.years)


def build_inputs(cfg: dict, states: list[PopulationState], data: Phase3Data, delta_shift: int = 0,
                 delta: np.ndarray | None = None, scale_factor: float | None = None) -> ModelInputs:
    """Assemble les entrées déterministes. `delta_shift` (+1, -1) donne les sensibilités de D16."""
    first = int(get_param(cfg, "horizon.start_year"))
    T = int(get_param(cfg, "horizon.flow_years"))
    if len(states) < T:
        raise ConfigError(f"Il faut au moins {T} états de population (reçu {len(states)}).")
    a0 = states[0].a0
    A = states[0].open_age
    years = np.arange(first, first + T)
    ages = np.arange(a0, A + 1)
    n = np.stack([st.n for st in states[:T]])                         # (T, C, S, K)
    tol = float(get_param(cfg, "tests.conservation_tolerance"))
    months = float(get_param(cfg, "wages.months_per_year"))
    advance = float(get_param(cfg, "pensions.indexation.stock_advance_factor_2024_to_2026"))

    # --- âge de départ et retraités (T8)
    dlt = cal.delta_from_config(cfg, delta_shift) if delta is None else np.asarray(delta, dtype=int)
    rho = retired_grid(years, ages, cfg, dlt)
    a_star = retirement_age_grid(years, ages, cfg, dlt)               # (T, C, S, K)
    rbar = rho_bar_fn(n, rho)

    # --- emploi conditionnel (D6, D16)
    f = float(get_param(cfg, "employment.observed_employment_rate.scale_factor")) if scale_factor is None else scale_factor
    e_obs = emp.scale_to_national_accounts(data.profile.e_obs[:, a0:], f)         # (S, K)
    e_base = emp.conditional_employment(e_obs[None, :, :], rbar, tol)             # (T, S, K)
    contributors = n * (1.0 - rho) * e_base[:, None, :, :]                        # (T, C, S, K)

    # --- salaires et assiette (D7-D10)
    w = wages.annual_gross_wages(cfg, ages)                                       # (C, S, K)
    assiette_base = (contributors * w[None]).sum(axis=(1, 2, 3))

    # --- stock / nouveaux liquidants
    t_idx = np.arange(T)[:, None, None, None]
    k_idx = np.arange(len(ages))[None, None, None, :]
    t_g = t_idx - k_idx - a0 + a_star                  # année de départ de la génération, relative à 2026 : g + a* - first
    # (g = year - age ; year = first + t ; age = a0 + k  =>  g + a* - first = t - (a0 + k) + a*)
    is_stock = (rho == 1.0) & (t_g <= 0)
    is_new = (rho == 1.0) & (t_g >= 1)
    if np.any(is_new & (t_g > t_idx)):
        raise AssertionError("Une génération ne peut pas partir après l'année courante tout en étant retraitée.")

    # pensions du stock : m1 x kappa x avance (x 12), recalées par lambda
    kappa = cal.kappa_from_drees(cfg)
    p_raw = cal.stock_pension_table(data.stock_m1, kappa, advance, months, a0)    # (C, S, K)
    age_first = (a0 + k_idx) - t_idx                                              # âge en 2026 de la même génération
    kk = np.clip(age_first - a0, 0, len(ages) - 1)[:, 0, 0, :]                      # (T, K) indices d'âge dans P
    p_cells = p_raw[:, :, kk]                                                     # (C, S, T, K)
    p_cells = np.moveaxis(p_cells, 2, 0)                                          # (T, C, S, K)
    b_initial = float((n[0] * rho[0] * p_cells[0]).sum())
    b_obs = cal.observed_stock_expenditure(data.stock_eff, data.stock_m1, data.stock_d13_factor, advance, months)
    lam_diag = cal.calibrate_lambda(b_obs, b_initial)
    lam = lam_diag["lambda"]
    pension_stock = lam * p_raw
    benefits_stock = (n * is_stock * lam * p_cells).sum(axis=(1, 2, 3))           # (T,)

    # theta : salaire à l'âge de départ de l'année de calibration (proxy D9)
    year_ref = int(get_param(cfg, "retirement.delta_effective_minus_legal.calibration_year"))
    legal_mean = cal.mean_legal_age_of_liquidants(data.new_eff, year_ref, cfg)
    dep_age = cal.round_half_up(legal_mean)[None, :] + dlt                       # (C, S)
    w_bar = np.take_along_axis(w, np.clip(dep_age - a0, 0, len(ages) - 1)[:, :, None], axis=2)[:, :, 0]
    theta = cal.calibrate_theta(data.new_eff, data.new_m1, kappa, lam, advance, months, w_bar)

    # nouveaux liquidants : matrice M[tau, t] = somme des N x theta x w(a*) des générations parties en tau
    w_dep = np.take_along_axis(np.broadcast_to(w[None], (T,) + w.shape),
                               np.clip(a_star - a0, 0, len(ages) - 1), axis=3)    # (T, C, S, K)
    weight = n * is_new * theta[None, :, :, None] * w_dep
    M = np.zeros((T, T))
    tt = np.broadcast_to(t_idx, is_new.shape)
    np.add.at(M, (t_g[is_new].astype(int), tt[is_new].astype(int)), weight[is_new])

    # perte d'emploi D16 (phi = 1) : cellules entièrement retraitées
    n_cell = n.sum(axis=1)                                                        # (T, S, K)
    e_full = np.broadcast_to(e_obs[None], n_cell.shape)
    fully = (1.0 - rbar) <= tol
    loss = (n_cell * e_full * fully).sum(axis=(1, 2))
    covered = (n_cell * e_full).sum(axis=(1, 2))

    diag = {"lambda": lam_diag, "kappa": kappa, "theta": theta, "scale_factor": f,
            "d13_factor": data.stock_d13_factor, "delta": dlt, "legal_mean": legal_mean,
            "retired_2026": float((n[0] * rho[0]).sum()), "retired_observed_eacr": float(data.stock_eff.sum() * data.stock_d13_factor)}
    return ModelInputs(years, ages, n, dlt, rho, rbar, e_base, contributors.sum(axis=(1, 2, 3)), assiette_base,
                       (n * rho).sum(axis=(1, 2, 3)), benefits_stock, M, w, pension_stock, theta, loss, covered, diag)


# ------------------------------------------------------------------------------------ exécution

@dataclass
class FinanceResult:
    years: np.ndarray             # (T,)
    contributors: np.ndarray      # (n_sim, T)
    retirees: np.ndarray          # (T,)
    ratio: np.ndarray             # (n_sim, T) cotisants par retraité
    assiette: np.ndarray          # (n_sim, T) A_t
    benefits: np.ndarray          # (n_sim, T) B_t
    contributions: np.ndarray     # (n_sim, T) C_t
    deficit: np.ndarray           # (n_sim, T) D_t
    reserve: np.ndarray           # (n_sim, T+1) R_2026 ... R_2066
    tau0: float
    k: float
    loss: np.ndarray              # (T,) perte d'emploi D16 (personnes), trajectoire centrale
    loss_share: np.ndarray        # (T,)
    diagnostics: dict


def employment_phi(macro_paths: macro.MacroPaths, cfg: dict) -> np.ndarray:
    """phi[sim, t] = (1 - u_t)/(1 - u_2025) (D18b)."""
    return emp.unemployment_factor(macro_paths.unemployment, float(get_param(cfg, "macro.unemployment_rate_2025")))


def run_finance(cfg: dict, inp: ModelInputs, paths: macro.MacroPaths, k: float | None = None,
                external_funding: float | None = None) -> FinanceResult:
    """Calcule A, B, C, D et R pour toutes les simulations à la fois (aucune boucle sur sim)."""
    T = inp.n_years
    if paths.n_years != T:
        raise ConfigError(f"Les trajectoires ont {paths.n_years} années, le modèle {T}.")
    tol = float(get_param(cfg, "tests.conservation_tolerance"))
    k = float(get_param(cfg, "finance.initial_reserve_k.reference")) if k is None else float(k)
    ext = float(get_param(cfg, "finance.external_funding_F")) if external_funding is None else float(external_funding)

    phi = employment_phi(paths, cfg)                                   # (n_sim, T)
    # T11 : e = phi x e_base doit rester dans [0, 1], pour chaque simulation et chaque année
    emp.check_rates(phi * inp.e_base.max(axis=(1, 2))[None, :], "taux d'emploi conditionnel (avec chômage)", tol)
    emp.check_rates(phi[:, :, None, None] * inp.e_base.min(axis=(1, 2))[None, :, None, None],
                    "taux d'emploi conditionnel (minimum)", tol)

    G = macro.wage_index(paths.productivity_growth)                    # (n_sim, T)
    assiette = G * phi * inp.assiette_base[None, :]
    contributors = phi * inp.contributors_base[None, :]
    benefits = inp.benefits_stock[None, :] + G @ inp.new_matrix       # (n_sim, T)

    # calibration sur la trajectoire de référence (première simulation) : D_2026 = 0 par construction
    ref = paths.reference()
    G_ref = macro.wage_index(ref.productivity_growth)
    phi_ref = employment_phi(ref, cfg)
    a_ref = (G_ref * phi_ref * inp.assiette_base[None, :])[0, 0]
    b_ref = (inp.benefits_stock[None, :] + G_ref @ inp.new_matrix)[0, 0]
    tau0 = cal.calibrate_tau0(float(b_ref), float(a_ref))

    contrib = contributions(tau0, assiette)
    d = deficit(benefits, contrib, ext)
    if np.any(np.abs(d[:, 0]) > tol * max(1.0, float(b_ref))):
        raise ConfigError("D_2026 n'est pas nul : toutes les simulations doivent partager les valeurs de 2026.")
    r0 = k * benefits[:, 0]
    R = reserves(r0, d, paths.real_return)

    retirees = inp.retirees
    ratio = contributors / retirees[None, :]
    loss = inp.loss_base * phi_ref[0]
    share = loss / (inp.covered_employment_base * phi_ref[0])
    diag = dict(inp.diagnostics)
    diag.update({"tau0": tau0, "benefits_2026": float(b_ref), "assiette_2026": float(a_ref)})
    return FinanceResult(inp.years, contributors, retirees, ratio, assiette, benefits, contrib, d, R, tau0, k,
                         loss, share, diag)
