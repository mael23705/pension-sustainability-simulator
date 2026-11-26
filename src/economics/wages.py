"""Salaires w[c, s, a] en euros bruts annuels 2026 (décisions D7, D8, D9, D10).

Chaque catégorie garde ses tranches d'âge, transformées en âges individuels par une fonction en
escalier (D10, aucune interpolation). Au-delà de la dernière tranche on garde sa valeur (D9 :
proxy du salaire à 62-64 ans, absorbé par theta). Les écarts entre sexes de la fonction publique
et des indépendants viennent de la moyenne de la catégorie, supposée indépendante de l'âge.
"""
from __future__ import annotations

import numpy as np

from config import ConfigError, categories, get_param
from conventions import N_SEXES, SEX_F, SEX_M

_SEX_KEY = {SEX_F: "F", SEX_M: "H"}


def price_factor(cfg: dict, reference_year: int, target_year: int = 2026) -> float:
    """Produit des (1 + inflation) des années reference_year + 1 à target_year (D8)."""
    infl = cfg["wages"]["inflation"]["values"]
    factor = 1.0
    for year in range(reference_year + 1, target_year + 1):
        if year not in infl:
            raise ConfigError(f"Inflation {year} absente de wages.inflation.values.")
        factor *= 1.0 + float(infl[year])
    return factor


def step_function(lower_bounds: list[int], values: list[float], ages: np.ndarray) -> np.ndarray:
    """Valeur de la tranche contenant chaque âge (fonction en escalier, tranches [b_i, b_{i+1}[)."""
    lower = np.asarray(lower_bounds)
    if len(lower) != len(values):
        raise ConfigError("Autant de bornes inférieures que de valeurs de tranche.")
    if np.any(np.diff(lower) <= 0):
        raise ConfigError("Les bornes de tranches doivent être strictement croissantes.")
    idx = np.clip(np.searchsorted(lower, ages, side="right") - 1, 0, len(values) - 1)
    return np.asarray(values, dtype=float)[idx]


def _sex_ratio(means: dict) -> np.ndarray:
    """(S,) rapport moyenne du sexe / moyenne de la catégorie."""
    return np.array([means[_SEX_KEY[s]] / means["all"] for s in (SEX_F, SEX_M)], dtype=float)


def net_monthly_by_category(cfg: dict, ages: np.ndarray) -> np.ndarray:
    """Salaire net mensuel moyen (C, S, K) dans l'unité de la source (euros courants de l'année de référence)."""
    cats = categories(cfg)
    ages = np.asarray(ages)
    out = np.zeros((len(cats), N_SEXES, len(ages)))
    w = cfg["wages"]

    for c, name in enumerate(cats):
        if name == "prive":
            blk = w["private"]
            for s in (SEX_F, SEX_M):
                out[c, s] = step_function(blk["age_band_lower_bounds"], blk["net_monthly_euros"][_SEX_KEY[s]], ages)
        elif name == "public":
            blk = w["public"]
            weights = blk["sub_sector_weights"]
            if abs(sum(weights.values()) - 1.0) > 1e-9:
                raise ConfigError("Les poids des sous-secteurs publics doivent sommer à 1.")
            profile = sum(weights[k] * step_function(blk["age_band_lower_bounds"], blk["net_monthly_euros"][k], ages)
                          for k in weights)
            out[c] = _sex_ratio(blk["sex_means_net_monthly"])[:, None] * profile[None, :]
        elif name == "independants":
            blk = w["independents"]
            profile = step_function(blk["age_band_lower_bounds"], blk["net_monthly_euros"], ages)
            out[c] = _sex_ratio(blk["sex_means_net_monthly"])[:, None] * profile[None, :]
        else:
            raise ConfigError(f"Catégorie sans table de salaires : {name!r}.")
    return out


def annual_gross_wages(cfg: dict, ages: np.ndarray) -> np.ndarray:
    """w[c, s, a] : salaire brut annuel en euros 2026 (net mensuel x brut/net x prix x 12), forme (C, S, K)."""
    cats = categories(cfg)
    net = net_monthly_by_category(cfg, ages)
    months = float(get_param(cfg, "wages.months_per_year"))
    keys = {"prive": ("private", "gross_to_net_private"),
            "public": ("public", "gross_to_net_public"),
            "independants": ("independents", "gross_to_net_independents")}
    out = np.empty_like(net)
    for c, name in enumerate(cats):
        block, ratio_key = keys[name]
        ratio = float(get_param(cfg, f"wages.{ratio_key}"))
        out[c] = net[c] * ratio * price_factor(cfg, int(cfg["wages"][block]["reference_year"])) * months
    if np.any(out <= 0):
        raise ConfigError("Un salaire nul ou négatif a été construit : vérifier wages dans le YAML.")
    return out
