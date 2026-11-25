"""Lecture et validation de config/assumptions.yaml.

Principe (docs/architecture.md, section 1) : aucun paramètre numérique dans le code.
Un paramètre `null` nécessaire à un calcul fait échouer l'exécution avec un message
clair ; il n'y a jamais de valeur par défaut silencieuse.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import yaml


class ConfigError(ValueError):
    """Paramètre absent, nul ou incohérent dans assumptions.yaml."""


def load_config(path: str | Path) -> dict:
    """Lit le fichier YAML et renvoie un dictionnaire."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {p}")
    with p.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ConfigError(f"{p} ne contient pas un dictionnaire YAML.")
    return cfg


def get_param(cfg: dict, dotted_path: str) -> Any:
    """Renvoie la valeur d'un paramètre, par exemple « demography.entry_age_a0 ».

    - Si le nœud final est de la forme {value: ..., status: ...}, on renvoie `value`.
    - Si la valeur est `null`, on lève ConfigError (pas de défaut silencieux).
    """
    node: Any = cfg
    for key in dotted_path.split("."):
        if not isinstance(node, dict) or key not in node:
            raise ConfigError(f"Paramètre absent de la configuration : {dotted_path!r}")
        node = node[key]
    if isinstance(node, dict) and "value" in node:
        node = node["value"]
    if node is None:
        raise ConfigError(
            f"Paramètre {dotted_path!r} nul (value: null) : à renseigner avant "
            "tout calcul qui en dépend."
        )
    return node


def conservation_tolerance(cfg: dict) -> float:
    """Tolérance numérique des tests de conservation (cahier 7.1)."""
    return float(get_param(cfg, "tests.conservation_tolerance"))


def categories(cfg: dict) -> list[str]:
    """Noms des catégories d'affiliation, dans l'ordre de l'axe `c`."""
    return list(get_param(cfg, "demography.categories"))


def affiliation_shares(cfg: dict, tol: float | None = None) -> np.ndarray:
    """Parts d'affiliation pi_c, dans l'ordre des catégories (test T12).

    Vérifie : somme égale à 1 et valeurs dans les plages `test_range` du YAML.
    """
    if tol is None:
        tol = conservation_tolerance(cfg)
    cats = categories(cfg)
    values = get_param(cfg, "demography.affiliation_shares_pi.values")
    ranges = cfg["demography"]["affiliation_shares_pi"].get("test_range", {})
    missing = [c for c in cats if c not in values]
    if missing:
        raise ConfigError(f"Parts pi_c manquantes pour : {missing}")
    pi = np.array([values[c] for c in cats], dtype=float)

    if abs(pi.sum() - 1.0) > tol:
        raise ConfigError(f"Les parts pi_c doivent sommer à 1 (somme = {pi.sum()}).")
    if (pi < 0).any():
        raise ConfigError("Une part pi_c est négative.")
    for c, p in zip(cats, pi):
        rng = ranges.get(c)
        if isinstance(rng, (list, tuple)) and len(rng) == 2:
            lo, hi = rng
            if not (lo <= p <= hi):
                raise ConfigError(
                    f"pi_{c} = {p} hors de la plage de test [{lo}, {hi}] "
                    "(docs/hypotheses.md)."
                )
    return pi


def raw_data_path(cfg: dict, root: str | Path, key: str) -> Path:
    """Chemin d'un fichier brut : `key` in {insee_population_file, insee_projection_file}."""
    return Path(root) / get_param(cfg, "data_files.raw_dir") / get_param(cfg, f"data_files.{key}")
