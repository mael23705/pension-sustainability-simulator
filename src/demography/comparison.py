"""Projection sur plusieurs années et comparaison avec une référence (cahier 7.3)."""
from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

from demography.engine import StepResult, step_year
from demography.population import PopulationState, YearParams


def run_projection(
    state0: PopulationState,
    params_for_year: Callable[[int, PopulationState], YearParams],
    first_year: int,
    n_steps: int,
    pi: np.ndarray,
    pi_mig: np.ndarray,
    overflow_policy: str = "raise",
) -> tuple[list[PopulationState], list[StepResult]]:
    """Enchaîne `n_steps` transitions à partir du 1er janvier `first_year`.

    `params_for_year(t, state)` renvoie les paramètres de l'année t (il reçoit l'état
    au 1er janvier t pour les calculs qui en dépendent).
    Renvoie (états aux 1er janvier first_year .. first_year + n_steps, résultats des étapes).
    """
    states = [state0]
    results: list[StepResult] = []
    for i in range(n_steps):
        t = first_year + i
        res = step_year(states[-1], params_for_year(t, states[-1]), pi, pi_mig, t, overflow_policy)
        states.append(res.state)
        results.append(res)
    return states, results


def age_group_totals(by_age: np.ndarray, groups: Sequence[Sequence[int]]) -> np.ndarray:
    """Effectifs par groupe d'âge [lo, hi] (bornes incluses) ; `by_age` : (..., ages)."""
    by_age = np.asarray(by_age, dtype=float)
    last = by_age.shape[-1] - 1
    out = [by_age[..., lo : min(hi, last) + 1].sum(axis=-1) for lo, hi in groups]
    return np.stack(out, axis=-1)


def relative_errors(model: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Erreur relative (modèle - référence) / référence, terme à terme."""
    model = np.asarray(model, dtype=float)
    reference = np.asarray(reference, dtype=float)
    return (model - reference) / reference
