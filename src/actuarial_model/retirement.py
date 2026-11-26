"""Part de retraités rho(a, g) (architecture : retired_share, test T8).

rho vaut 0 ou 1 : un individu de la génération g est retraité à l'âge a si a >= âge légal
de sa génération + écart delta (âge effectif moins âge légal, constant sur l'horizon).
L'âge légal vient du tableau `retirement.legal_age_by_generation.integer` du YAML
(COR, tableau 1.4). L'écart `delta` est calibré en phase 3 : il est donc un **argument
obligatoire**, jamais une valeur par défaut.
"""
from __future__ import annotations

import numpy as np

from config import get_param


def legal_age(generation: int, cfg: dict) -> int:
    """Âge légal d'ouverture des droits (entier) de la génération `generation`."""
    block = cfg["retirement"]["legal_age_by_generation"]
    table = block["integer"]
    if generation in table:
        return int(table[generation])
    first, last = min(table), max(table)
    if generation < first:
        return int(get_param(cfg, "retirement.legal_age_by_generation.earlier_generations"))
    if generation > last:
        return int(get_param(cfg, "retirement.legal_age_by_generation.later_generations"))
    raise KeyError(f"Génération {generation} absente du tableau des âges légaux.")


def retired_share(age: int, generation: int, cfg: dict, delta_years: int) -> float:
    """rho in {0, 1} : 1 si l'âge atteint l'âge légal de la génération plus `delta_years`."""
    return 1.0 if age >= legal_age(generation, cfg) + delta_years else 0.0


# ---------------------------------------------------------------------------------------------
# Version vectorisée (phase 3) : même règle que `retired_share`, appliquée à des grilles entières.
# Axes : t = année, c = catégorie, s = sexe, k = âge (de a0 à A, classe ouverte au dernier indice).
# ---------------------------------------------------------------------------------------------

def legal_age_array(generations: np.ndarray, cfg: dict) -> np.ndarray:
    """Âge légal entier de chaque génération d'un tableau (même forme que `generations`)."""
    gens = np.asarray(generations, dtype=int)
    table = {int(g): legal_age(int(g), cfg) for g in np.unique(gens)}
    flat = np.array([table[int(g)] for g in gens.ravel()], dtype=int)
    return flat.reshape(gens.shape)


def retirement_age_grid(years: np.ndarray, ages: np.ndarray, cfg: dict, delta: np.ndarray) -> np.ndarray:
    """Âge de départ a*(c, s, t, k) = âge légal de la génération (t - a) + delta[c, s] ; forme (T, C, S, K).

    La classe ouverte (dernier âge) est rattachée à la génération t - A (convention du moteur).
    """
    years = np.asarray(years, dtype=int)
    ages = np.asarray(ages, dtype=int)
    legal = legal_age_array(years[:, None] - ages[None, :], cfg)          # (T, K)
    delta = np.asarray(delta, dtype=int)                                  # (C, S)
    return legal[:, None, None, :] + delta[None, :, :, None]


def retired_grid(years: np.ndarray, ages: np.ndarray, cfg: dict, delta: np.ndarray) -> np.ndarray:
    """rho in {0, 1} de forme (T, C, S, K) : 1 si l'âge atteint l'âge de départ de la génération (T8)."""
    a_star = retirement_age_grid(years, ages, cfg, delta)
    return (np.asarray(ages, dtype=int)[None, None, None, :] >= a_star).astype(np.float64)


def rho_bar(n: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """rho agrégé sur les catégories avec les effectifs présents (D16) ; forme (T, S, K).

    Une cellule sans effectif reçoit la valeur 1 (rien à cotiser) : elle n'intervient dans aucun total.
    """
    num = (n * rho).sum(axis=1)
    den = n.sum(axis=1)
    out = np.ones_like(den)
    np.divide(num, den, out=out, where=den > 0)
    return out
