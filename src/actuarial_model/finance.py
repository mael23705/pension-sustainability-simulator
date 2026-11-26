"""Bilan annuel : cotisations, déficit et réserve (cahier 4.2).

C_t = tau A_t ;  D_t = B_t - C_t - F_t ;  R_{t+1} = R_t (1 + r_t) - D_t.
Tous les tableaux ont l'axe des simulations en tête : forme (n_sim, T). La boucle ne porte que
sur les années, jamais sur les simulations.
"""
from __future__ import annotations

import numpy as np


def contributions(tau: float, assiette: np.ndarray) -> np.ndarray:
    """C_t = tau x A_t."""
    return tau * np.asarray(assiette, dtype=float)


def deficit(benefits: np.ndarray, contrib: np.ndarray, external_funding: np.ndarray | float = 0.0) -> np.ndarray:
    """D_t = B_t - C_t - F_t (positif = déficit)."""
    return np.asarray(benefits, dtype=float) - np.asarray(contrib, dtype=float) - external_funding


def reserves(r0: np.ndarray | float, d: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Trajectoire R[sim, 0..T] : R_{t+1} = R_t (1 + r_t) - D_t, avec R[:, 0] = R_2026 = r0.

    `d` et `r` ont la forme (n_sim, T) ; `r0` est un scalaire ou un vecteur (n_sim,).
    """
    d = np.asarray(d, dtype=float)
    r = np.asarray(r, dtype=float)
    if d.shape != r.shape or d.ndim != 2:
        raise ValueError("D et r doivent avoir la même forme (n_sim, T).")
    n_sim, n_years = d.shape
    out = np.empty((n_sim, n_years + 1))
    out[:, 0] = r0
    for t in range(n_years):                      # boucle sur les années seulement
        out[:, t + 1] = out[:, t] * (1.0 + r[:, t]) - d[:, t]
    return out
