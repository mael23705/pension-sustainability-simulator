"""Attribution des catégories d'affiliation (parts pi_c), décision D2/D3.

Les catégories (privé, public, indépendants) n'existent qu'à partir de l'âge a0.
En dessous, la population n'est pas segmentée (N_pre).
"""
from __future__ import annotations

import numpy as np


def assign_to_categories(flow: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """Répartit un effectif entre catégories selon les parts pi_c.

    `flow` a la forme (...) (par exemple (S,) ou (S, K)) ; le résultat a la forme
    (C, ...). On a toujours : somme sur c du résultat == flow (test T4/T5).
    """
    pi = np.asarray(pi, dtype=float)
    flow = np.asarray(flow, dtype=float)
    shape = (pi.shape[0],) + (1,) * flow.ndim
    return pi.reshape(shape) * flow[None, ...]
