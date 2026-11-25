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
