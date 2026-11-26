"""Trajectoires macroéconomiques : productivité, chômage, rendement des réserves (axe [sim, t]).

Décision D18 : transition linéaire de 2026 à 2040 vers les cibles de long terme du COR.
Toutes les trajectoires sont des tableaux de forme (n_sim, T) : la boucle du modèle porte sur
les années, jamais sur les simulations (docs/architecture.md).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from config import ConfigError, get_param


def linear_transition(start_value: float, end_value: float, start_year: int, end_year: int,
                      years: np.ndarray) -> np.ndarray:
    """Valeur linéaire de `start_value` (à start_year) à `end_value` (à end_year), constante ensuite.

    Avant `start_year` la valeur est celle de `start_year` (aucune extrapolation).
    """
    if end_year <= start_year:
        raise ConfigError("La transition exige end_year > start_year.")
    x = np.clip((np.asarray(years, dtype=float) - start_year) / (end_year - start_year), 0.0, 1.0)
    return start_value + x * (end_value - start_value)


def long_term_values(cfg: dict, scenario: str = "central") -> tuple[float, float]:
    """(croissance de la productivité, taux de chômage) de long terme d'un scénario de sensibilité."""
    sens = cfg["macro"]["long_term_sensitivity"]
    if scenario not in sens:
        raise ConfigError(f"Scénario inconnu : {scenario!r} (attendus : {sorted(sens)}).")
    return float(sens[scenario]["productivity_growth"]), float(sens[scenario]["unemployment_rate"])


def productivity_path(cfg: dict, years: np.ndarray, scenario: str = "central") -> np.ndarray:
    """g_t : croissance réelle annuelle de la productivité (et des salaires), vecteur (T,)."""
    g_end, _ = long_term_values(cfg, scenario)
    tr = cfg["macro"]["transition_to_long_term"]
    return linear_transition(float(get_param(cfg, "macro.productivity_growth_2026")), g_end,
                             int(tr["start_year"]), int(tr["end_year"]), years)


def unemployment_path(cfg: dict, years: np.ndarray, scenario: str = "central") -> np.ndarray:
    """u_t : taux de chômage, vecteur (T,)."""
    _, u_end = long_term_values(cfg, scenario)
    tr = cfg["macro"]["transition_to_long_term"]
    return linear_transition(float(get_param(cfg, "macro.unemployment_rate_2026")), u_end,
                             int(tr["start_year"]), int(tr["end_year"]), years)


def wage_index(growth: np.ndarray) -> np.ndarray:
    """Indice réel des salaires G[..., t] : G = 1 à la première année, puis produit des (1 + g_t).

    `growth[..., t]` est la croissance de l'année t par rapport à t - 1 ; celle de la première
    année concerne 2025 -> 2026 et n'intervient pas (les salaires sont déjà en euros 2026).
    """
    growth = np.asarray(growth, dtype=float)
    if np.any(growth <= -1.0):
        raise ConfigError("Une croissance <= -100 % n'a pas de sens.")
    factors = growth.copy()
    factors[..., 0] = 0.0
    return np.cumprod(1.0 + factors, axis=-1)


@dataclass(frozen=True)
class MacroPaths:
    """Trajectoires par simulation, toutes de forme (n_sim, T)."""

    productivity_growth: np.ndarray
    unemployment: np.ndarray
    real_return: np.ndarray

    def __post_init__(self) -> None:
        shapes = {self.productivity_growth.shape, self.unemployment.shape, self.real_return.shape}
        if len(shapes) != 1 or len(next(iter(shapes))) != 2:
            raise ValueError("Les trois trajectoires doivent avoir la même forme (n_sim, T).")

    @property
    def n_sim(self) -> int:
        return self.productivity_growth.shape[0]

    @property
    def n_years(self) -> int:
        return self.productivity_growth.shape[1]

    @classmethod
    def from_config(cls, cfg: dict, years: np.ndarray, n_sim: int = 1, scenario: str = "central",
                    real_return: float | None = None) -> "MacroPaths":
        """Trajectoire du YAML recopiée sur `n_sim` simulations identiques (sans aléa en phase 3)."""
        r = float(get_param(cfg, "finance.real_return_on_reserves")) if real_return is None else real_return
        tile = lambda v: np.tile(np.asarray(v, dtype=float), (n_sim, 1))
        return cls(tile(productivity_path(cfg, years, scenario)),
                   tile(unemployment_path(cfg, years, scenario)),
                   np.full((n_sim, len(years)), r))

    def with_real_return(self, r: np.ndarray) -> "MacroPaths":
        """Même trajectoire de productivité et de chômage, autre rendement réel (n_sim, T)."""
        return MacroPaths(self.productivity_growth, self.unemployment, np.asarray(r, dtype=float))

    def reference(self) -> "MacroPaths":
        """Première simulation, au format (1, T) : trajectoire de calibration de tau0."""
        return MacroPaths(self.productivity_growth[:1], self.unemployment[:1], self.real_return[:1])
