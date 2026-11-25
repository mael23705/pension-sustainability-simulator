"""Part de retraités rho(a, g) (architecture : retired_share, test T8).

rho vaut 0 ou 1 : un individu de la génération g est retraité à l'âge a si a >= âge légal
de sa génération + écart delta (âge effectif moins âge légal, constant sur l'horizon).
L'âge légal vient du tableau `retirement.legal_age_by_generation.integer` du YAML
(COR, tableau 1.4). L'écart `delta` est calibré en phase 3 : il est donc un **argument
obligatoire**, jamais une valeur par défaut.
"""
from __future__ import annotations

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
