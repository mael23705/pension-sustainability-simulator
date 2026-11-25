"""Lecture des fichiers Insee : POP3 (population au 1er janvier 2026) et projection 2026.

Fichiers (fiches 1 à 5 de docs/donnees.md) :
- `3_Pop1janv_age.xlsx`, onglet « 2026 » : population par âge révolu au 1er janvier ;
- `00_central.xlsx` (scénario central) : populations, quotients de mortalité, fécondité,
  soldes migratoires, ajustement et naissances, par année de 1962 à 2070.

Les positions des lignes sont repérées par leurs étiquettes (pas par des numéros de ligne
écrits en dur) et chaque bloc est vérifié ; en cas d'écart, on lève une erreur au lieu de
corriger en silence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from conventions import INSEE_FERTILITY_UNIT, INSEE_MORTALITY_UNIT, N_SEXES, SEX_F, SEX_M
from demography.population import YearParams

# Structure des fichiers Insee (faits de format, pas des paramètres du modèle).
LAST_DETAILED_AGE = 105     # la projection s'arrête à « 105 ans ou plus »
LAST_QUOTIENT_AGE = 120     # quotients de mortalité jusqu'à 120 ans
FERTILITY_FIRST_AGE = 15    # fécondité par âge atteint, de 15 à 50 ans
FERTILITY_LAST_AGE = 50


# --------------------------------------------------------------------------------------
# Population au 1er janvier 2026 (POP3)
# --------------------------------------------------------------------------------------
def load_population_2026(path: str | Path, sheet: str = "2026", champ: str = "France") -> np.ndarray:
    """Renvoie N_init[s, a] (s = 0 femmes, 1 hommes ; a = 0..105 ; 105 = « 105 ou plus »).

    `champ` = « France » (France entière, y compris Mayotte depuis 2014) ou
    « France métropolitaine ». L'âge est l'âge **révolu au 1er janvier**.
    Vérifie que la somme égale le total publié dans l'onglet (sinon ValueError).
    """
    raw = pd.read_excel(path, sheet_name=str(sheet), header=None)
    label0 = raw.iloc[:, 0].astype(str).str.strip()

    head = label0.index[label0 == "Année de naissance"]
    if len(head) != 1:
        raise ValueError("Ligne d'en-têtes « Année de naissance » introuvable ou multiple.")
    h = int(head[0])

    groups = raw.iloc[h - 1].astype(str).str.strip()
    cols = groups.index[groups == champ]
    if len(cols) != 1:
        raise ValueError(f"Bloc de colonnes {champ!r} introuvable dans l'onglet {sheet}.")
    c = int(cols[0])
    expected = ["Ensemble", "Hommes", "Femmes"]
    found = [str(v).strip() for v in raw.iloc[h, c : c + 3]]
    if found != expected:
        raise ValueError(f"En-têtes inattendus {found} (attendu {expected}).")

    total_row = label0.index[label0 == "Population totale"]
    if len(total_row) != 1:
        raise ValueError("Ligne « Population totale » introuvable.")
    r_tot = int(total_row[0])

    body = raw.iloc[h + 1 : r_tot, [1, c, c + 1, c + 2]].dropna(how="all")
    n_ages = LAST_DETAILED_AGE + 1
    if len(body) != n_ages:
        raise ValueError(f"{len(body)} lignes d'âge lues, {n_ages} attendues.")
    if not str(body.iloc[-1, 0]).startswith(str(LAST_DETAILED_AGE)):
        raise ValueError("La dernière ligne d'âge doit être « 105 ou plus ».")
    if [int(v) for v in body.iloc[:-1, 0]] != list(range(LAST_DETAILED_AGE)):
        raise ValueError("Les âges ne sont pas consécutifs de 0 à 104.")

    men = body.iloc[:, 2].astype(float).to_numpy()
    women = body.iloc[:, 3].astype(float).to_numpy()
    both = body.iloc[:, 1].astype(float).to_numpy()
    n_init = np.empty((N_SEXES, n_ages))
    n_init[SEX_F], n_init[SEX_M] = women, men

    published = float(raw.iloc[r_tot, c])
    if not np.isclose(n_init.sum(), published, rtol=0, atol=0.5):
        raise ValueError(f"Somme {n_init.sum()} différente du total publié {published}.")
    if not np.allclose(women + men, both, rtol=0, atol=0.5):
        raise ValueError("Hommes + femmes ne reproduit pas la colonne « Ensemble ».")
    return n_init


# --------------------------------------------------------------------------------------
# Projection 2026, scénario central
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class InseeProjection:
    years: np.ndarray            # (Y,)
    population: np.ndarray       # (S, 106, Y) âge révolu au 1er janvier, 105 = « 105 ou plus »
    mortality: np.ndarray        # (S, 121, Y) quotients (probabilités) par âge atteint
    fertility: np.ndarray        # (36, Y) naissances par femme, âge atteint 15..50
    net_migration: np.ndarray    # (S, 121, Y) solde migratoire par âge atteint
    adjustment: np.ndarray       # (S, 121, Y) « ajustement » par âge atteint
    births_total: np.ndarray     # (Y,)
    births_girls: np.ndarray     # (Y,)

    def year_index(self, year: int) -> int:
        idx = np.nonzero(self.years == year)[0]
        if len(idx) != 1:
            raise ValueError(f"Année {year} absente de la projection.")
        return int(idx[0])


def _sheet(xl: pd.ExcelFile, name: str) -> pd.DataFrame:
    return pd.read_excel(xl, sheet_name=name, header=None)


def _years_and_columns(df: pd.DataFrame) -> tuple[np.ndarray, list[int]]:
    """Années de la ligne 1 et positions des colonnes correspondantes."""
    row = df.iloc[1, 1:]
    mask = row.notna().to_numpy()
    years = row[mask].astype(float).astype(int).to_numpy()
    cols = [j + 1 for j in np.nonzero(mask)[0]]
    return years, cols


def _unique_row(df: pd.DataFrame, *, equals: str | None = None, startswith: str | None = None) -> int:
    col0 = df.iloc[:, 0].astype(str).str.strip()
    mask = col0 == equals if equals is not None else col0.str.startswith(startswith)
    idx = col0.index[mask]
    if len(idx) != 1:
        raise ValueError(f"Étiquette {equals or startswith!r} : {len(idx)} occurrence(s), 1 attendue.")
    return int(idx[0])


def _block(df: pd.DataFrame, first_row: int, n_rows: int, cols: list[int],
           first_label: float, last_label: float) -> np.ndarray:
    """Bloc numérique (n_rows, n_cols) dont les étiquettes de lignes sont vérifiées."""
    labels = df.iloc[first_row : first_row + n_rows, 0]
    if float(labels.iloc[0]) != first_label or float(labels.iloc[-1]) != last_label:
        raise ValueError(
            f"Étiquettes de lignes inattendues ({labels.iloc[0]} .. {labels.iloc[-1]}), "
            f"attendu {first_label} .. {last_label}."
        )
    return df.iloc[first_row : first_row + n_rows, cols].astype(float).to_numpy()


def load_central_projection(path: str | Path) -> InseeProjection:
    """Charge la projection Insee 2026 (scénario central) : populations et hypothèses."""
    xl = pd.ExcelFile(path)

    pop_sheets = {SEX_F: "populationF", SEX_M: "populationH"}
    mort_sheets = {SEX_F: "hyp_mortaliteF", SEX_M: "hyp_mortaliteH"}
    mig_sheets = {SEX_F: "hyp_soldemigF", SEX_M: "hyp_soldemigH"}
    adj_sheets = {SEX_F: "ajustementF", SEX_M: "ajustementH"}

    ref = _sheet(xl, "populationF")
    years, cols = _years_and_columns(ref)
    n_years = len(years)

    population = np.empty((N_SEXES, LAST_DETAILED_AGE + 1, n_years))
    mortality = np.empty((N_SEXES, LAST_QUOTIENT_AGE + 1, n_years))
    migration = np.empty((N_SEXES, LAST_QUOTIENT_AGE + 1, n_years))
    adjustment = np.empty((N_SEXES, LAST_QUOTIENT_AGE + 1, n_years))

    for s in (SEX_F, SEX_M):
        df = _sheet(xl, pop_sheets[s])
        _check_same_years(years, df, pop_sheets[s])
        r_last = _unique_row(df, equals=f"{LAST_DETAILED_AGE}+")
        population[s] = _population_block(df, r_last, cols)

        df = _sheet(xl, mort_sheets[s])
        _check_same_years(years, df, mort_sheets[s])
        r_title = _unique_row(df, startswith="Quotients de mortalité pour 100 000 par âge atteint")
        mortality[s] = _block(df, r_title + 1, LAST_QUOTIENT_AGE + 1, cols, 0, LAST_QUOTIENT_AGE) \
            / INSEE_MORTALITY_UNIT

        for target, sheets in ((migration, mig_sheets), (adjustment, adj_sheets)):
            df = _sheet(xl, sheets[s])
            _check_same_years(years, df, sheets[s])
            target[s] = _block(df, 2, LAST_QUOTIENT_AGE + 1, cols, 0, LAST_QUOTIENT_AGE)

    df = _sheet(xl, "hyp_fecondite")
    _check_same_years(years, df, "hyp_fecondite")
    n_f = FERTILITY_LAST_AGE - FERTILITY_FIRST_AGE + 1
    fertility = _block(df, 2, n_f, cols, FERTILITY_FIRST_AGE, FERTILITY_LAST_AGE) / INSEE_FERTILITY_UNIT

    df = _sheet(xl, "naissance")
    _check_same_years(years, df, "naissance")
    births_total = df.iloc[_unique_row(df, equals="Total des naissances"), cols].astype(float).to_numpy()
    births_girls = df.iloc[_unique_row(df, equals="dont naissances de filles"), cols].astype(float).to_numpy()

    return InseeProjection(years, population, mortality, fertility, migration, adjustment,
                           births_total, births_girls)


def _population_block(df: pd.DataFrame, r_last: int, cols: list[int]) -> np.ndarray:
    """Lignes d'âges 0..104 puis « 105+ » (étiquette texte pour la dernière)."""
    first = r_last - LAST_DETAILED_AGE
    labels = df.iloc[first:r_last, 0]
    if [int(v) for v in labels] != list(range(LAST_DETAILED_AGE)):
        raise ValueError("Âges de l'onglet de population non consécutifs de 0 à 104.")
    return df.iloc[first : r_last + 1, cols].astype(float).to_numpy()


def _check_same_years(years: np.ndarray, df: pd.DataFrame, name: str) -> None:
    other, _ = _years_and_columns(df)
    if not np.array_equal(years, other):
        raise ValueError(f"Onglet {name} : années différentes de celles de l'onglet population.")


# --------------------------------------------------------------------------------------
# Agrégation de la classe ouverte et paramètres annuels pour le moteur
# --------------------------------------------------------------------------------------
def aggregate_open_class(values: np.ndarray, open_age: int) -> np.ndarray:
    """Regroupe les âges >= open_age dans une classe ouverte (dernier axe = âge).

    Entrée (..., n) avec n > open_age ; sortie (..., open_age + 1) dont la dernière colonne
    est la somme des colonnes open_age..n-1. Testé dans tests/test_insee_io.py.
    """
    values = np.asarray(values, dtype=float)
    if not (0 <= open_age < values.shape[-1]):
        raise ValueError("open_age hors des âges disponibles.")
    out = np.empty(values.shape[:-1] + (open_age + 1,))
    out[..., :open_age] = values[..., :open_age]
    out[..., open_age] = values[..., open_age:].sum(axis=-1)
    return out


def open_class_quotient(q_atteint: np.ndarray, population_by_age: np.ndarray, open_age: int) -> np.ndarray:
    """Quotient de la classe ouverte, moyenne pondérée par la population du 1er janvier.

    Pour un âge révolu a au 1er janvier (a >= open_age), le quotient pertinent est celui de
    l'âge atteint a+1 ; pour « 105 ou plus » on retient celui de l'âge atteint 106
    (convention documentée). `q_atteint` : (S, 121) ; `population_by_age` : (S, 106).
    """
    ages = np.arange(open_age, LAST_DETAILED_AGE + 1)
    q_ages = np.minimum(ages + 1, LAST_DETAILED_AGE + 1)  # âge atteint correspondant
    q = q_atteint[:, q_ages]                              # (S, n)
    w = population_by_age[:, open_age : LAST_DETAILED_AGE + 1]
    if np.any(w.sum(axis=1) <= 0):
        raise ValueError("Population de la classe ouverte nulle : pondération impossible.")
    return (q * w).sum(axis=1) / w.sum(axis=1)


def year_params(
    proj: InseeProjection, year: int, open_age: int,
    population_by_age: np.ndarray | None = None, include_adjustment: bool = True,
) -> YearParams:
    """Paramètres de l'année `year` pour le moteur, à partir de la projection Insee.

    - Quotients : « âge atteint » ; l'âge révolu a au 1er janvier correspond à l'âge atteint a+1.
    - Fécondité : taux de l'âge atteint a+1 appliqué aux femmes d'âge révolu a.
    - Migrations : solde (+ ajustement si `include_adjustment`) par âge atteint ; les âges
      atteints >= open_age sont regroupés dans la classe ouverte.
    - Pondération de la classe ouverte : population Insee du 1er janvier `year`, sauf si
      `population_by_age` est fourni.
    """
    iy = proj.year_index(year)
    q_att = proj.mortality[:, :, iy]
    weights = proj.population[:, :, iy] if population_by_age is None else population_by_age

    q_age = np.full((N_SEXES, open_age + 1), np.nan)
    q_age[:, 1 : open_age + 1] = q_att[:, 1 : open_age + 1]

    fert = np.zeros(open_age + 1)
    for k, a_att in enumerate(range(FERTILITY_FIRST_AGE, FERTILITY_LAST_AGE + 1)):
        a = a_att - 1
        if a > open_age:
            raise ValueError("La classe ouverte est dans les âges féconds : non géré.")
        fert[a] += proj.fertility[k, iy]

    flows = proj.net_migration[:, :, iy]
    if include_adjustment:
        flows = flows + proj.adjustment[:, :, iy]

    return YearParams(
        q_birth=q_att[:, 0].copy(),
        q_age=q_age,
        q_open=open_class_quotient(q_att, weights, open_age),
        fertility=fert,
        girl_share=float(proj.births_girls[iy] / proj.births_total[iy]),
        net_migration=aggregate_open_class(flows, open_age),
    )
