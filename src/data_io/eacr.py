"""Lecture des tables dérivées de l'EACR (Drees) : stock de retraités, nouveaux liquidants, âge conjoncturel.

Les fichiers de `data/processed/` sont reconstruits par `scripts/build_eacr_tables.py` à partir
du classeur EACR (fiche 10 de docs/donnees.md). Ils ont les colonnes `sexe` (T, F, H), `age`
(entier, ou les lignes de total « Ensemble » et « plus de 95 »), `effectifs` et `m1`
(avantage principal moyen de droit direct, euros par mois, perçu en décembre).

Convention d'axes : s = 0 femmes, s = 1 hommes ; a = âge de 0 à A (A = classe ouverte).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from conventions import N_SEXES, SEX_F, SEX_M

SEX_CODE = {SEX_F: "F", SEX_M: "H"}


def _read(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Table dérivée introuvable : {p}. La reconstruire avec scripts/build_eacr_tables.py "
            "(fichier EACR dans data/raw/)."
        )
    return pd.read_csv(p, dtype={"sexe": str, "age": str})


def load_by_age(path: str | Path) -> pd.DataFrame:
    """Lignes d'âge individuel (colonnes sexe, age entier, effectifs, m1), sans les lignes de total."""
    df = _read(path)
    df = df[df["age"].str.fullmatch(r"\d+")].copy()
    df["age"] = df["age"].astype(int)
    # m1 absent (secret statistique, quelques personnes par ligne) : la ligne est écartée des effectifs
    # comme des montants, pour que effectifs x m1 reste cohérent ; le nombre de personnes écartées est publié.
    missing = df["m1"].isna()
    df.attrs["n_dropped_rows"] = int(missing.sum())
    df.attrs["n_dropped_people"] = int(df.loc[missing, "effectifs"].sum())
    return df.loc[~missing].copy()


def load_total_row(path: str | Path, sex: str = "T") -> tuple[float, float]:
    """(effectifs, m1) de la ligne « Ensemble » pour le sexe demandé (D13 : niveau de référence)."""
    df = _read(path)
    row = df[(df["sexe"] == sex) & (df["age"] == "Ensemble")]
    if len(row) != 1:
        raise ValueError(f"Ligne « Ensemble » absente ou dupliquée pour le sexe {sex!r} dans {path}.")
    return float(row["effectifs"].iloc[0]), float(row["m1"].iloc[0])


def arrays_by_sex_age(df: pd.DataFrame, open_age: int) -> tuple[np.ndarray, np.ndarray]:
    """Effectifs (S, A+1) et avantage moyen m1 (S, A+1) par sexe et âge de 0 à A.

    Les âges >= A sont agrégés dans la classe ouverte ; son m1 est la moyenne pondérée par les
    effectifs. Les âges absents du fichier ont un effectif nul et un m1 nul.
    """
    eff = np.zeros((N_SEXES, open_age + 1))
    amount = np.zeros((N_SEXES, open_age + 1))      # somme effectifs x m1
    for s, code in SEX_CODE.items():
        d = df[df["sexe"] == code]
        for a, n, m in zip(d["age"].to_numpy(), d["effectifs"].to_numpy(float), d["m1"].to_numpy(float)):
            k = min(int(a), open_age)
            eff[s, k] += n
            amount[s, k] += n * m
    m1 = np.divide(amount, eff, out=np.zeros_like(amount), where=eff > 0)
    return eff, m1


def stock_arrays(path: str | Path, open_age: int) -> tuple[np.ndarray, np.ndarray, float]:
    """Stock EACR 2024 : effectifs (S, A+1), m1 (S, A+1) et facteur de remise à l'échelle D13.

    D13 : l'écart entre la somme des âges individuels et la ligne « Ensemble » n'est pas corrigé
    dans les poids relatifs ; le niveau est ramené à la ligne « Ensemble » par un facteur unique,
    renvoyé pour être publié (environ 1,007).
    """
    df = load_by_age(path)
    eff, m1 = arrays_by_sex_age(df, open_age)
    total_row, _ = load_total_row(path, "T")
    return eff, m1, float(total_row / eff.sum())


def new_retirees_arrays(path: str | Path, open_age: int) -> tuple[np.ndarray, np.ndarray]:
    """Nouveaux liquidants de 2024 : effectifs (S, A+1) et m1 (S, A+1)."""
    return arrays_by_sex_age(load_by_age(path), open_age)


def load_conjunctural_age(path: str | Path) -> pd.DataFrame:
    """Âge conjoncturel de départ 2024 par caisse et sexe (colonnes caisse, sexe, ageconj)."""
    return _read(path)
