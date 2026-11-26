"""Calibrations de la phase 3 (décisions D17, D19, D20) : delta, kappa, lambda, theta, tau0.

Chaque fonction est pure : elle prend des tableaux et des paramètres du YAML, et renvoie des
tableaux ou un petit dictionnaire de diagnostics à publier. Aucune valeur n'est écrite en dur.
Axes : c = catégorie, s = sexe, a = âge.
"""
from __future__ import annotations

import numpy as np

from actuarial_model.retirement import legal_age
from config import ConfigError, categories, get_param
from conventions import N_SEXES, SEX_F, SEX_M

_SEX_KEY = {SEX_F: "F", SEX_M: "H"}


def round_half_up(x):
    """Arrondi à l'entier le plus proche, 0,5 vers le haut (convention D5)."""
    return np.floor(np.asarray(x, dtype=float) + 0.5).astype(int)


# --------------------------------------------------------------------------- delta (D19)

def mean_legal_age_of_liquidants(eff_new: np.ndarray, year: int, cfg: dict) -> np.ndarray:
    """Âge légal moyen (S,) des générations qui partaient en `year`, pondéré par les nouveaux liquidants.

    `eff_new[s, a]` : liquidants par sexe et âge **atteint au 31 décembre** de `year` (EACR) ; la
    génération est donc `year - a`. Les âges >= A (classe ouverte du tableau) sont négligeables.
    """
    ages = np.arange(eff_new.shape[1])
    legal = np.array([legal_age(int(year - a), cfg) for a in ages], dtype=float)
    w = eff_new.sum(axis=1)
    if np.any(w <= 0):
        raise ConfigError("Aucun nouveau liquidant : impossible de calculer l'âge légal moyen.")
    return (eff_new * legal[None, :]).sum(axis=1) / w


def effective_age_reference(cfg: dict) -> dict[str, np.ndarray | None]:
    """Âges effectifs moyens de 2024 du YAML, par catégorie : vecteur (S,) ou None (pas de mesure)."""
    ref = cfg["retirement"]["delta_effective_minus_legal"]["reference_effective_age_2024"]
    priv = ref["private_general_regime"]
    pub = float(get_param(cfg, "retirement.delta_effective_minus_legal.reference_effective_age_2024.public_proxy"))
    return {
        "prive": np.array([priv["female"], priv["male"]], dtype=float),
        "public": np.array([pub, pub], dtype=float),
        "independants": None,
    }


def calibrate_delta(cfg: dict, eff_new: np.ndarray, year: int = 2024) -> dict:
    """delta_{c,s} = âge effectif moyen de `year` - âge légal moyen des générations de `year` (D19).

    Renvoie {'real': (C, S) réels, 'integer': (C, S) entiers (arrondi D5), 'legal_mean': (S,)}.
    Faute de mesure (indépendants), le YAML donne une valeur provisoire (`provisional_values`).
    """
    cats = categories(cfg)
    legal_mean = mean_legal_age_of_liquidants(eff_new, year, cfg)
    ref = effective_age_reference(cfg)
    provisional = cfg["retirement"]["delta_effective_minus_legal"].get("provisional_values", {})
    real = np.zeros((len(cats), N_SEXES))
    for c, name in enumerate(cats):
        if ref.get(name) is not None:
            real[c] = ref[name] - legal_mean
        elif name in provisional:
            real[c] = float(provisional[name])
        else:
            raise ConfigError(f"Aucun âge effectif de référence ni valeur provisoire pour {name!r}.")
    return {"real": real, "integer": round_half_up(real), "legal_mean": legal_mean}


def delta_from_config(cfg: dict, shift: int = 0) -> np.ndarray:
    """delta_{c,s} entiers (C, S) lus dans le YAML, décalés de `shift` années (sensibilité D16)."""
    block = get_param(cfg, "retirement.delta_effective_minus_legal")
    out = np.zeros((len(categories(cfg)), N_SEXES), dtype=int)
    for c, name in enumerate(categories(cfg)):
        for s in (SEX_F, SEX_M):
            out[c, s] = int(block[name][_SEX_KEY[s]])
    return out + int(shift)


# --------------------------------------------------------------------------- kappa (D17)

def kappa_from_drees(cfg: dict) -> np.ndarray:
    """kappa_{c,s} : pension moyenne de la catégorie c et du sexe s / pension moyenne du sexe s (tous retraités).

    La pension moyenne d'une catégorie est la moyenne des régimes principaux rattachés, pondérée par
    leurs effectifs (tableaux 3 et 4 du panorama DREES 2026). Niveau relatif seulement : un niveau
    commun est absorbé par lambda.
    """
    block = cfg["pensions"]["stock_breakdown"]["drees_table_3_4"]
    cats = categories(cfg)
    kappa = np.zeros((len(cats), N_SEXES))
    for c, name in enumerate(cats):
        regimes = [r for r in block["regimes"].values() if r["category"] == name]
        if not regimes:
            raise ConfigError(f"Aucun régime DREES rattaché à la catégorie {name!r}.")
        for s in (SEX_F, SEX_M):
            key = _SEX_KEY[s]
            eff = np.array([r["effectifs"][key] for r in regimes], dtype=float)
            pen = np.array([r["pension"][key] for r in regimes], dtype=float)
            kappa[c, s] = (eff * pen).sum() / eff.sum() / float(block["all_retirees"]["pension"][key])
    return kappa


# --------------------------------------------------------------------------- stock, lambda (D17)

def stock_pension_table(m1: np.ndarray, kappa: np.ndarray, advance: float, months: float, a0: int) -> np.ndarray:
    """Pension annuelle du stock avant recalage, p[c, s, k] pour k = âge - a0 : m1 x kappa x avance x 12."""
    return months * advance * kappa[:, :, None] * m1[None, :, a0:]


def observed_stock_expenditure(eff: np.ndarray, m1: np.ndarray, d13_factor: float, advance: float,
                               months: float) -> float:
    """B_obs de 2026 : somme des effectifs x m1 (âges individuels), remise au niveau « Ensemble » (D13), avancée."""
    return float(months * advance * d13_factor * (eff * m1).sum())


def calibrate_lambda(b_obs: float, b_initial: float) -> dict:
    """lambda = B_obs / B_initial, avec les diagnostics à publier (D17).

    `lambda` n'est pas un paramètre libre : c'est un indicateur de cohérence de l'ensemble (effectifs
    du moteur, répartition par catégorie, niveau de m1). Un écart important se publie, il ne se corrige pas.
    """
    if b_initial <= 0 or b_obs <= 0:
        raise ConfigError("B_obs et B_initial doivent être strictement positifs pour calibrer lambda.")
    lam = b_obs / b_initial
    return {"lambda": lam, "expenditure_before": b_initial, "expenditure_after": b_initial * lam,
            "reference_total": b_obs, "gap_percent": 100.0 * (b_initial - b_obs) / b_obs}


# --------------------------------------------------------------------------- theta (D17, D20)

def calibrate_theta(eff_new: np.ndarray, m1_new: np.ndarray, kappa: np.ndarray, lam: float,
                    advance: float, months: float, w_bar: np.ndarray) -> np.ndarray:
    """theta_{c,s} = pension annuelle des nouveaux liquidants / salaire annuel à l'âge de départ (D20).

    La pension d'un nouveau liquidant de sexe s et de catégorie c est m1_s moyen des liquidants de 2024
    x kappa_{c,s} x avance x lambda x 12 (même chaîne que le stock : continuité entre stock et flux).
    `w_bar[c, s]` : salaire annuel brut en euros 2026 à l'âge de départ (proxy D9).
    """
    n = eff_new.sum(axis=1)
    if np.any(n <= 0):
        raise ConfigError("Nouveaux liquidants nuls : theta non calibrable.")
    m1_mean = (eff_new * m1_new).sum(axis=1) / n                      # (S,)
    pension = months * advance * lam * kappa * m1_mean[None, :]       # (C, S)
    if np.any(w_bar <= 0):
        raise ConfigError("Salaire de départ nul ou négatif : theta non calibrable.")
    return pension / w_bar


# --------------------------------------------------------------------------- tau0

def calibrate_tau0(b_2026: float, a_2026: float) -> float:
    """tau0 = B_2026 / A_2026 : taux de calibration (D_2026 = 0), pas un taux légal."""
    if a_2026 <= 0:
        raise ConfigError("Assiette nulle en 2026 : tau0 n'est pas défini.")
    return float(b_2026 / a_2026)
