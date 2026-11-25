"""Migrations en flux bruts (m+ arrivées, m- départs), solde préservé.

Règles (reprise-phase-2, section 4 ; cahier 3.7) :
- la source (Insee) ne donne que le solde par âge et sexe ; on pose m+ = max(solde, 0)
  et m- = max(-solde, 0), donc m+ - m- = solde ;
- les arrivées sont réparties selon pi_mig (a >= a0) ; en dessous de a0, elles vont dans
  la population non segmentée ;
- les départs sont prélevés sur les catégories au prorata des effectifs présents ;
- ni les arrivées ni les départs ne sont soumis à la mortalité l'année du mouvement ;
- si les départs dépassent l'effectif présent : alerte dans le journal, jamais de
  troncature silencieuse. Politique « raise » (par défaut) : exception ;
  politique « log_only » : alerte journalisée, effectif possiblement négatif (le test T2
  le détectera).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from conventions import SEX_LABELS
from demography.population import PopulationState

POLICIES = ("raise", "log_only")


class MigrationOverflowError(RuntimeError):
    """Départs migratoires supérieurs à l'effectif présent."""


@dataclass
class Alert:
    year: int
    code: str
    message: str
    details: dict = field(default_factory=dict)


def split_gross_flows(net: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(m_plus, m_minus) avec m_plus - m_minus == net."""
    net = np.asarray(net, dtype=float)
    return np.maximum(net, 0.0), np.maximum(-net, 0.0)


def check_policy(policy: str) -> None:
    if policy not in POLICIES:
        raise ValueError(f"Politique de dépassement inconnue : {policy!r} (attendu : {POLICIES}).")


def _report_overflow(
    dep: np.ndarray, present: np.ndarray, ages: np.ndarray, year: int,
    policy: str, alerts: list[Alert], where: str,
) -> None:
    bad = dep > present
    if not bad.any():
        return
    for s, k in zip(*np.nonzero(bad)):
        alerts.append(
            Alert(
                year=year,
                code="migration_overflow",
                message=(
                    f"Départs ({dep[s, k]:.6g}) supérieurs à l'effectif présent "
                    f"({present[s, k]:.6g}) : {SEX_LABELS[s]}, âge {int(ages[k])} ({where})."
                ),
                details={"sex": int(s), "age": int(ages[k]), "departures": float(dep[s, k]),
                         "present": float(present[s, k])},
            )
        )
    if policy == "raise":
        raise MigrationOverflowError(alerts[-1].message + f" ({int(bad.sum())} cas au total)")


def apply_migrations(
    state: PopulationState, net: np.ndarray, pi_mig: np.ndarray, year: int,
    policy: str, alerts: list[Alert],
) -> tuple[PopulationState, float]:
    """Applique les soldes migratoires des âges 1..A (l'âge 0 est traité avec les naissances).

    `net` a la forme (S, A+1). Renvoie (nouvel état, solde appliqué = somme m+ - somme m-).
    """
    check_policy(policy)
    a0 = state.a0
    new = state.copy()
    m_plus, m_minus = split_gross_flows(net)

    # --- âges 1..a0-1 : population non segmentée ---
    if a0 > 1:
        ages = np.arange(1, a0)
        present = new.n_pre[:, 1:a0]
        _report_overflow(m_minus[:, 1:a0], present, ages, year, policy, alerts, "non segmenté")
        new.n_pre[:, 1:a0] = present + m_plus[:, 1:a0] - m_minus[:, 1:a0]

    # --- âges a0..A : départs au prorata des catégories, arrivées selon pi_mig ---
    ages = np.arange(a0, state.open_age + 1)
    dep = m_minus[:, a0:]
    arr = m_plus[:, a0:]
    n = new.n
    tot = n.sum(axis=0)  # (S, K)
    _report_overflow(dep, tot, ages, year, policy, alerts, "catégories")

    positive = tot > 0
    ratio = np.divide(dep, tot, out=np.zeros_like(dep), where=positive)
    n_after = n * (1.0 - ratio)[None, ...]
    # Cas dégénéré (effectif nul, départs > 0) : seulement atteint en politique log_only.
    leftover = np.where(positive, 0.0, dep)
    n_after = n_after - pi_mig[:, None, None] * leftover[None, ...]
    n_after = n_after + pi_mig[:, None, None] * arr[None, ...]
    new.n = n_after

    applied = float(m_plus[:, 1:].sum() - m_minus[:, 1:].sum())
    return new, applied


def apply_age0_migration(
    newborn_survivors: np.ndarray, net0: np.ndarray, year: int,
    policy: str, alerts: list[Alert],
) -> tuple[np.ndarray, float]:
    """Solde migratoire de l'âge atteint 0, appliqué aux nouveau-nés survivants.

    Convention (docs/conventions-moteur.md) : à l'âge 0, la classe n'existe qu'une fois les
    naissances versées ; le solde de l'âge 0 est donc appliqué à ce moment-là.
    """
    check_policy(policy)
    m_plus, m_minus = split_gross_flows(net0)
    _report_overflow(
        m_minus[:, None], newborn_survivors[:, None], np.array([0]), year, policy, alerts,
        "nouveau-nés",
    )
    out = newborn_survivors + m_plus - m_minus
    return out, float(m_plus.sum() - m_minus.sum())
