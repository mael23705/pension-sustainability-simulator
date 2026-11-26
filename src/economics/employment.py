"""Taux d'emploi : profil par âge et sexe, facteur d'échelle, chômage et taux conditionnel.

Décisions : D6 (niveau = comptabilité nationale, profil = enquête Emploi 2025), D16 (taux
conditionnel aux non-retraités), D18b (lien avec le chômage). Aucune troncature : un taux
conditionnel hors de [0, 1] est une erreur, jamais une valeur plafonnée (test T11).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from conventions import N_SEXES, SEX_F, SEX_M

_SEX_CODE = {"F": SEX_F, "H": SEX_M}
_AGE_SINGLE = re.compile(r"Y(\d{2})$")
_AGE_BAND = re.compile(r"Y(\d{2})T(\d{2})$")
_AGE_OPEN = re.compile(r"Y_GE(\d{2})$")


class EmploymentError(ValueError):
    """Taux d'emploi incohérent (hors de [0, 1]) : le scénario est rejeté, jamais corrigé."""


@dataclass(frozen=True)
class EmploymentProfile:
    """Profil observé par sexe et âge de 0 à A (les âges avant 15 ans ont un taux nul)."""

    e_obs: np.ndarray            # (S, A+1) taux d'emploi sur la population totale de l'âge
    survey_employment: float     # emploi total de l'enquête, en personnes (tous âges de 15 ans et plus)


def load_employment_profile(path: str | Path, open_age: int) -> EmploymentProfile:
    """Lit `taux-emploi-age-sexe-2025.csv` (script `build_employment_table.py`).

    Les âges individuels de 15 à 64 ans sont repris tels quels ; les tranches 65-69, 70-74 et
    75 ans ou plus sont étendues à chaque âge qu'elles couvrent (fonction en escalier, D10).
    Les tranches de recoupement (15-19, 20-24, etc.) servent de contrôle et sont ignorées.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Table d'emploi introuvable : {p}. La reconstruire avec scripts/build_employment_table.py."
        )
    df = pd.read_csv(p, dtype={"age": str, "sexe": str})
    e_obs = np.zeros((N_SEXES, open_age + 1))
    total = 0.0
    for row in df.itertuples(index=False):
        s = _SEX_CODE.get(row.sexe)
        if s is None:
            continue
        rate = row.taux_emploi_pct / 100.0
        pop = row.population_milliers * 1000.0
        m_single = _AGE_SINGLE.match(row.age)
        m_band = _AGE_BAND.match(row.age)
        m_open = _AGE_OPEN.match(row.age)
        if m_single and 15 <= int(m_single.group(1)) <= 64:
            a = int(m_single.group(1))
            e_obs[s, a] = rate
            total += rate * pop
        elif m_band and int(m_band.group(1)) >= 65:
            lo, hi = int(m_band.group(1)), int(m_band.group(2))
            e_obs[s, lo : min(hi, open_age) + 1] = rate
            total += rate * pop
        elif m_open and int(m_open.group(1)) >= 75:
            e_obs[s, int(m_open.group(1)) :] = rate
            total += rate * pop
    return EmploymentProfile(e_obs=e_obs, survey_employment=total)


def scale_factor(survey_employment: float, national_accounts_total: float) -> float:
    """Facteur unique f tel que f x emploi de l'enquête = emploi de la comptabilité nationale (D6)."""
    if survey_employment <= 0 or national_accounts_total <= 0:
        raise EmploymentError("Les deux totaux d'emploi doivent être strictement positifs.")
    return float(national_accounts_total / survey_employment)


def scale_to_national_accounts(e_obs: np.ndarray, factor: float) -> np.ndarray:
    """Applique le facteur d'échelle ; le résultat doit rester dans [0, 1] (T11)."""
    scaled = np.asarray(e_obs, dtype=float) * factor
    check_rates(scaled, "taux d'emploi observé après mise à l'échelle")
    return scaled


def unemployment_factor(u_t: np.ndarray, u_ref: float) -> np.ndarray:
    """Rapport (1 - u_t) / (1 - u_ref) de D18b ; `u_t` de forme quelconque, par exemple (sim, t)."""
    u_t = np.asarray(u_t, dtype=float)
    if np.any(u_t < 0) or np.any(u_t >= 1) or not (0 <= u_ref < 1):
        raise EmploymentError("Un taux de chômage doit être dans [0, 1[.")
    return (1.0 - u_t) / (1.0 - u_ref)


def unemployment_adjusted(e_obs: np.ndarray, u_t: float, u_ref: float) -> np.ndarray:
    """e_obs_t = e_obs_ref x (1 - u_t)/(1 - u_ref) (D18b) ; erreur si le résultat sort de [0, 1]."""
    out = np.asarray(e_obs, dtype=float) * unemployment_factor(np.asarray(u_t), u_ref)
    check_rates(out, "taux d'emploi observé ajusté du chômage")
    return out


def check_rates(e: np.ndarray, label: str, tol: float = 1e-9) -> None:
    """Lève EmploymentError si une valeur est hors de [0, 1] (ou non finie). Jamais de plafonnement."""
    e = np.asarray(e, dtype=float)
    if not np.all(np.isfinite(e)):
        raise EmploymentError(f"{label} : valeurs non finies.")
    if e.min() < -tol or e.max() > 1.0 + tol:
        raise EmploymentError(
            f"{label} hors de [0, 1] : minimum {e.min():.6g}, maximum {e.max():.6g}. "
            "Le scénario est incompatible avec la convention D16/D18b ; aucune troncature."
        )


def conditional_employment(e_obs: np.ndarray, rho_bar: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    """Taux conditionnel e = e_obs / (1 - rho_bar) (D16), emploi des retraités nul.

    - si 1 - rho_bar <= tol (cellule entièrement retraitée) : e = 0 ;
    - sinon e = e_obs / (1 - rho_bar), et une valeur hors de [0, 1] lève EmploymentError (T11).
    `e_obs` et `rho_bar` se diffusent (broadcasting) l'un sur l'autre.
    """
    e_obs = np.asarray(e_obs, dtype=float)
    rho_bar = np.asarray(rho_bar, dtype=float)
    check_rates(e_obs, "taux d'emploi observé")
    if np.any(rho_bar < -tol) or np.any(rho_bar > 1.0 + tol):
        raise EmploymentError("rho_bar doit être dans [0, 1].")
    retired = (1.0 - rho_bar) <= tol
    denom = np.where(retired, 1.0, 1.0 - rho_bar)
    e = np.where(retired, 0.0, e_obs / denom)
    check_rates(e, "taux d'emploi conditionnel")
    return e


def employment_loss(population: np.ndarray, e_obs: np.ndarray, rho_bar: np.ndarray, tol: float = 1e-9):
    """Perte d'emploi de D16 : personnes en emploi observé dans les cellules entièrement retraitées.

    `population` : effectifs de la cellule (toutes catégories), même forme que `rho_bar`.
    Renvoie (perte en personnes, emploi observé couvert en personnes) ; la part est leur rapport.
    """
    population = np.asarray(population, dtype=float)
    observed = population * np.asarray(e_obs, dtype=float)
    retired = (1.0 - np.asarray(rho_bar, dtype=float)) <= tol
    return float(observed[retired].sum()), float(observed.sum())
