"""Outils de test : construction du cas jouet à partir du bloc `toy_example` du YAML."""
from __future__ import annotations

import numpy as np

from conventions import SEX_F, SEX_M
from demography.population import PopulationState, YearParams

SEX_KEY = {SEX_F: "F", SEX_M: "M"}


def toy_pi(cfg: dict) -> np.ndarray:
    return np.array(cfg["toy_example"]["pi"], dtype=float)


def toy_state(cfg: dict) -> PopulationState:
    """État initial du cas jouet : n_pre (S, 1), n (3, S, 2)."""
    toy = cfg["toy_example"]
    cats = toy["categories"]
    n_pre = np.array([[toy["initial_pre"][SEX_KEY[s]][0]] for s in (SEX_F, SEX_M)], dtype=float)
    n = np.zeros((len(cats), 2, toy["open_class_age"] - toy["entry_age_a0"] + 1))
    for c, name in enumerate(cats):
        for s in (SEX_F, SEX_M):
            n[c, s, :] = toy["initial_by_category"][SEX_KEY[s]][name]
    return PopulationState(n_pre, n)


def toy_params(cfg: dict, year: int) -> YearParams:
    """Paramètres de l'année `year` du cas jouet."""
    toy = cfg["toy_example"]
    y = toy["years"][year]
    open_age = toy["open_class_age"]
    q_age = np.full((2, open_age + 1), np.nan)
    for s in (SEX_F, SEX_M):
        q_age[s, 1:] = y["q_age"][SEX_KEY[s]]
    pick = lambda key: np.array([y[key][SEX_KEY[s]] for s in (SEX_F, SEX_M)], dtype=float)
    return YearParams(
        q_birth=pick("q_birth"),
        q_age=q_age,
        q_open=pick("q_open"),
        fertility=np.array(y["fertility"], dtype=float),
        girl_share=float(y["girl_share"]),
        net_migration=np.array([y["net_migration"][SEX_KEY[s]] for s in (SEX_F, SEX_M)], dtype=float),
    )


def random_state_and_params(rng: np.random.Generator, n_cat: int = 3, a0: int = 3, open_age: int = 9):
    """État et paramètres aléatoires (tests de propriétés ; valeurs de test uniquement)."""
    n_pre = rng.uniform(50, 150, size=(2, a0))
    n = rng.uniform(50, 150, size=(n_cat, 2, open_age - a0 + 1))
    q_age = np.full((2, open_age + 1), np.nan)
    q_age[:, 1:] = rng.uniform(0.0, 0.3, size=(2, open_age))
    fert = np.zeros(open_age + 1)
    fert[2:6] = rng.uniform(0.0, 0.3, size=4)
    params = YearParams(
        q_birth=rng.uniform(0.0, 0.1, size=2),
        q_age=q_age,
        q_open=rng.uniform(0.0, 0.5, size=2),
        fertility=fert,
        girl_share=0.49,
        net_migration=rng.uniform(-5, 5, size=(2, open_age + 1)),
    )
    pi = rng.dirichlet(np.ones(n_cat))
    return PopulationState(n_pre, n), params, pi


def toy_finance_setup(cfg: dict, flow_years: int | None = None):
    """Cas jouet financier : renvoie (cfg_jouet, états de population, données, trajectoires macro).

    Le YAML réel est copié puis remplacé, bloc par bloc, par les valeurs du bloc `toy_finance`
    (statut toy_example) : un seul âge de retraite (2), salaires constants, facteurs de prix égaux à 1.
    """
    import copy

    from actuarial_model.model import Phase3Data
    from demography.comparison import run_projection
    from economics.employment import EmploymentProfile
    from economics.macro import MacroPaths

    tf = cfg["toy_finance"]
    toy = copy.deepcopy(cfg)
    n_years = tf["flow_years"] if flow_years is None else flow_years
    toy["horizon"]["flow_years"]["value"] = n_years
    toy["demography"]["categories"] = list(cfg["toy_example"]["categories"])
    toy["tests"]["conservation_tolerance"] = cfg["tests"]["conservation_tolerance"]
    toy["retirement"]["legal_age_by_generation"] = {
        "integer": {2000: tf["legal_age_all_generations"]},
        "earlier_generations": tf["legal_age_all_generations"],
        "later_generations": tf["legal_age_all_generations"],
    }
    toy["retirement"]["delta_effective_minus_legal"]["value"] = {
        c: {"F": 0, "H": 0} for c in toy["demography"]["categories"]}
    toy["retirement"]["delta_effective_minus_legal"]["calibration_year"] = {"value": 2024}
    toy["employment"]["observed_employment_rate"]["scale_factor"] = {"value": 1.0}
    toy["macro"]["unemployment_rate_2025"] = {"value": tf["unemployment_rate_2025"]}
    toy["pensions"]["indexation"]["stock_advance_factor_2024_to_2026"] = {"value": 1.0}
    w = tf["wages_annual_gross"]
    ones = {"F": 1.0, "H": 1.0, "all": 1.0}
    toy["wages"] = {
        "months_per_year": {"value": 1},
        "gross_to_net_private": {"value": 1.0}, "gross_to_net_public": {"value": 1.0},
        "gross_to_net_independents": {"value": 1.0},
        "inflation": {"values": {}},
        "private": {"reference_year": 2026, "age_band_lower_bounds": [0],
                    "net_monthly_euros": {"F": [w["prive"]["F"]], "H": [w["prive"]["H"]]}},
        "public": {"reference_year": 2026, "age_band_lower_bounds": [0],
                   "net_monthly_euros": {"fpe": [100.0], "fpt": [100.0], "fph": [100.0]},
                   "sub_sector_weights": {"fpe": 1.0, "fpt": 0.0, "fph": 0.0},
                   "sex_means_net_monthly": {"F": w["public"]["F"], "H": w["public"]["H"],
                                             "all": 100.0}},
        "independents": {"reference_year": 2026, "age_band_lower_bounds": [0],
                         "net_monthly_euros": [80.0],
                         "sex_means_net_monthly": {"F": w["independants"]["F"], "H": w["independants"]["H"], "all": 80.0}},
    }
    pen, all_pen = tf["kappa_pensions"], tf["all_retirees_pension"]
    toy["pensions"]["stock_breakdown"]["drees_table_3_4"] = {
        "all_retirees": {"effectifs": {"F": 1, "H": 1}, "pension": {"F": all_pen, "H": all_pen}},
        "regimes": {c: {"category": c, "effectifs": {"F": 1, "H": 1}, "pension": {"F": pen[c], "H": pen[c]}}
                    for c in toy["demography"]["categories"]},
    }

    state0 = toy_state(cfg)
    pi = toy_pi(cfg)
    states, _ = run_projection(state0, lambda t, _s: toy_params(cfg, t), 2026, 2, pi, pi)   # états de 2026, 2027 et 2028

    arr = lambda d: np.array([d["F"], d["H"]], dtype=float)
    data = Phase3Data(stock_eff=arr(tf["stock"]["effectifs"]), stock_m1=arr(tf["stock"]["m1"]), stock_d13_factor=1.0,
                      new_eff=arr(tf["new_retirees"]["effectifs"]), new_m1=arr(tf["new_retirees"]["m1"]),
                      profile=EmploymentProfile(e_obs=arr(tf["employment_profile"]), survey_employment=1.0))
    base = lambda key: np.array([tf["paths"][key]], dtype=float)
    if n_years > len(tf["paths"]["real_return"]):          # années supplémentaires : dernière valeur reconduite
        extend = lambda a: np.concatenate([a, np.repeat(a[:, -1:], n_years - a.shape[1], axis=1)], axis=1)
        paths = MacroPaths(extend(base("productivity_growth")), extend(base("unemployment")), extend(base("real_return")))
    else:
        paths = MacroPaths(base("productivity_growth"), base("unemployment"), base("real_return"))
    return toy, states, data, paths
