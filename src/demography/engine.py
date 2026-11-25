"""Transition annuelle t -> t+1 (calendrier : mortalité -> vieillissement -> migrations -> naissances).

Conventions (cahier 3.7, reprise-phase-2 section 4, docs/conventions-moteur.md) :
- les flux de l'année t se calculent sur la population au 1er janvier t ;
- les naissances viennent des femmes présentes au 1er janvier t et sont versées dans la
  classe d'âge 0 au 1er janvier t+1, après application du quotient de mortalité de l'âge 0 ;
- le solde migratoire de l'âge 0 est appliqué aux nouveau-nés (étape « naissances ») ;
- la mortalité est identique pour toutes les catégories (v0.1).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from conventions import SEX_F
from demography.categories import assign_to_categories
from demography.migration import (
    Alert, apply_age0_migration, apply_migrations, check_policy,
)
from demography.population import PopulationState, YearParams

STEP_ORDER = ("mortalite", "vieillissement", "migrations", "naissances")


@dataclass
class StepResult:
    state: PopulationState          # population au 1er janvier t+1
    alerts: list[Alert] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)   # étapes dans l'ordre d'exécution (T6)
    births: float = 0.0             # naissances vivantes avant mortalité de l'âge 0
    deaths: float = 0.0             # décès de l'année parmi la population au 1er janvier t
    net_migration_applied: float = 0.0  # somme m+ - somme m- effectivement appliquée


def survival_factors(params: YearParams, open_age: int) -> np.ndarray:
    """Facteur de survie par sexe et âge au 1er janvier : (S, A+1).

    Pour a < A : 1 - q_age[a+1] (la personne atteint l'âge a+1 dans l'année).
    Pour a = A : 1 - q_open (elle reste dans la classe ouverte).
    """
    surv = np.empty_like(params.q_age)
    surv[:, :open_age] = 1.0 - params.q_age[:, 1 : open_age + 1]
    surv[:, open_age] = 1.0 - params.q_open
    return surv


def apply_mortality(state: PopulationState, params: YearParams) -> tuple[PopulationState, float]:
    """Étape 1 : survivants par classe d'âge au 1er janvier (les indices ne bougent pas encore)."""
    surv = survival_factors(params, state.open_age)
    new = PopulationState(
        state.n_pre * surv[:, : state.a0],
        state.n * surv[None, :, state.a0 :],
    )
    return new, state.total() - new.total()


def age_population(survivors: PopulationState, pi: np.ndarray) -> PopulationState:
    """Étape 2 : vieillissement d'un an.

    - n_pre[a] -> n_pre[a+1] ; la classe 0 est laissée vide (remplie à l'étape naissances) ;
    - les survivants de a0-1 entrent dans les catégories à l'âge a0 selon pi ;
    - la classe ouverte A reçoit les survivants de A-1 et ceux de la classe A (test T7).
    """
    n_pre = np.zeros_like(survivors.n_pre)
    n_pre[:, 1:] = survivors.n_pre[:, :-1]

    n = np.zeros_like(survivors.n)
    n[:, :, 1:] = survivors.n[:, :, :-1]
    n[:, :, -1] += survivors.n[:, :, -1]                       # classe ouverte : on y reste
    n[:, :, 0] += assign_to_categories(survivors.n_pre[:, -1], pi)  # entrée à a0
    return PopulationState(n_pre, n)


def compute_births(state: PopulationState, params: YearParams) -> np.ndarray:
    """Naissances par sexe (S,) calculées sur les femmes présentes au 1er janvier t."""
    women = state.by_age()[SEX_F]
    total = float((params.fertility * women).sum())
    return np.array([total * params.girl_share, total * (1.0 - params.girl_share)])


def step_year(
    state: PopulationState, params: YearParams, pi: np.ndarray, pi_mig: np.ndarray,
    year: int, overflow_policy: str = "raise",
) -> StepResult:
    """Population au 1er janvier t+1 à partir de celle du 1er janvier t."""
    check_policy(overflow_policy)
    params.validate(state.open_age)
    result = StepResult(state=state)

    births_by_sex = compute_births(state, params)  # flux de t sur la population du 1er janvier t

    survivors, deaths = apply_mortality(state, params)
    result.trace.append("mortalite")
    result.deaths = deaths

    aged = age_population(survivors, pi)
    result.trace.append("vieillissement")

    migrated, applied = apply_migrations(
        aged, params.net_migration, pi_mig, year, overflow_policy, result.alerts
    )
    result.trace.append("migrations")

    newborn_survivors = births_by_sex * (1.0 - params.q_birth)
    deaths_newborn = float(births_by_sex.sum() - newborn_survivors.sum())
    newborns, applied0 = apply_age0_migration(
        newborn_survivors, params.net_migration[:, 0], year, overflow_policy, result.alerts
    )
    migrated.n_pre[:, 0] = newborns
    result.trace.append("naissances")

    result.state = migrated
    result.births = float(births_by_sex.sum())
    result.deaths = deaths + deaths_newborn
    result.net_migration_applied = applied + applied0
    return result
