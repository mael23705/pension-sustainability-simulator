"""Structures de données de la population (docs/architecture.md, section 4).

Convention : tous les tableaux sont en float64 ; s = 0 femmes, s = 1 hommes.
- N_pre[s, a]  pour a < a0 (population non segmentée) ;
- N[c, s, i]   pour a = a0 + i, de a0 jusqu'à A (classe ouverte, dernier indice).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from conventions import N_SEXES
from demography.categories import assign_to_categories


@dataclass
class PopulationState:
    """Population au 1er janvier d'une année."""

    n_pre: np.ndarray  # (S, a0)
    n: np.ndarray      # (C, S, A - a0 + 1)

    def __post_init__(self) -> None:
        self.n_pre = np.asarray(self.n_pre, dtype=np.float64)
        self.n = np.asarray(self.n, dtype=np.float64)
        if self.n_pre.ndim != 2 or self.n.ndim != 3:
            raise ValueError("n_pre doit être (S, a0) et n doit être (C, S, K).")
        if self.n_pre.shape[0] != self.n.shape[1]:
            raise ValueError("n_pre et n n'ont pas le même nombre de sexes.")
        if self.n_pre.shape[1] < 1:
            raise ValueError("a0 doit valoir au moins 1.")

    @property
    def a0(self) -> int:
        return self.n_pre.shape[1]

    @property
    def open_age(self) -> int:
        """Âge A de la classe ouverte (A et plus)."""
        return self.a0 + self.n.shape[2] - 1

    @property
    def n_categories(self) -> int:
        return self.n.shape[0]

    def by_age(self) -> np.ndarray:
        """Population par sexe et âge, toutes catégories confondues : (S, A+1)."""
        out = np.empty((self.n.shape[1], self.open_age + 1))
        out[:, : self.a0] = self.n_pre
        out[:, self.a0 :] = self.n.sum(axis=0)
        return out

    def total(self) -> float:
        return float(self.n_pre.sum() + self.n.sum())

    def copy(self) -> "PopulationState":
        return PopulationState(self.n_pre.copy(), self.n.copy())


@dataclass(frozen=True)
class YearParams:
    """Paramètres démographiques de l'année t (flux calculés sur la population au 1er janvier t).

    q_birth[s]      quotient de mortalité de l'âge atteint 0 (nouveau-nés de l'année) ;
    q_age[s, a]     quotient de l'âge atteint a, pour a = 1..A (colonne 0 non utilisée, NaN) :
                    probabilité de décéder dans l'année pour qui est a-1 au 1er janvier
                    (et passe à l'âge a pendant l'année) ;
    q_open[s]       quotient des personnes déjà dans la classe ouverte au 1er janvier ;
    fertility[a]    naissances par femme d'âge révolu a au 1er janvier (0 hors âges féconds) ;
    girl_share      part des filles parmi les naissances ;
    net_migration[s, a]  solde migratoire de l'âge atteint a (classe a au 1er janvier t+1),
                    a = 0..A ; la classe A regroupe les âges atteints >= A.
    """

    q_birth: np.ndarray
    q_age: np.ndarray
    q_open: np.ndarray
    fertility: np.ndarray
    girl_share: float
    net_migration: np.ndarray

    def validate(self, open_age: int) -> None:
        S, width = self.q_age.shape
        if S != N_SEXES or width != open_age + 1:
            raise ValueError(f"q_age doit être de forme ({N_SEXES}, {open_age + 1}).")
        if self.net_migration.shape != (S, open_age + 1):
            raise ValueError("net_migration doit être de forme (S, A+1).")
        if self.fertility.shape != (open_age + 1,):
            raise ValueError("fertility doit être de forme (A+1,).")
        for name, arr in (
            ("q_birth", self.q_birth),
            ("q_age[:, 1:]", self.q_age[:, 1:]),
            ("q_open", self.q_open),
        ):
            if not np.all(np.isfinite(arr)):
                raise ValueError(f"{name} contient des valeurs non finies (année manquante ?).")
            if np.any(arr < 0) or np.any(arr > 1):
                raise ValueError(f"{name} doit être dans [0, 1].")
        if not np.all(np.isfinite(self.net_migration)):
            raise ValueError("net_migration contient des valeurs non finies (année manquante ?).")
        if not np.all(np.isfinite(self.fertility)) or np.any(self.fertility < 0):
            raise ValueError("fertility doit être finie et positive.")
        if not (0.0 <= self.girl_share <= 1.0):
            raise ValueError("girl_share doit être dans [0, 1].")


def initial_population(by_age_open: np.ndarray, a0: int, pi: np.ndarray) -> PopulationState:
    """Population initiale N_pre, N à partir d'un tableau (S, A+1) (classe ouverte déjà agrégée).

    Règle documented_hypothesis (YAML : initial_population_shares) : pour a >= a0, chaque
    catégorie reçoit la part pi_c de l'effectif de l'âge et du sexe.
    """
    by_age_open = np.asarray(by_age_open, dtype=np.float64)
    if not (1 <= a0 <= by_age_open.shape[1] - 1):
        raise ValueError("a0 doit vérifier 1 <= a0 <= A.")
    n_pre = by_age_open[:, :a0].copy()
    n = assign_to_categories(by_age_open[:, a0:], pi)
    return PopulationState(n_pre, n)
