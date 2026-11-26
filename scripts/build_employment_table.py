"""Étape 3 (phase 3) : reconstruit le tableau des taux d'emploi par âge et sexe (enquête Emploi 2025).

Usage (depuis la racine du dépôt) :  python scripts/build_employment_table.py [chemin_du_zip]
Lit le zip de l'Insee SANS le décompresser et écrit data/processed/taux-emploi-age-sexe-2025.csv
(ignoré par Git). Méthode : docs/donnees.md, fiche 6 (« Taux d'emploi par âge individuel »).

    e_obs(s, a) = PT_EMPSTA_IN_POP(s, a) / ( POP(s, a) / POP(ensemble, a) )

PT_EMPSTA_IN_POP est la part des personnes en emploi dans la population TOTALE de l'âge (les deux
sexes), d'où la division par la part du sexe s dans la population de l'âge a.
"""
import sys
import zipfile
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
ZIP_PAR_DEFAUT = RACINE / "data" / "raw" / "DD_EEC_ANNUEL_2025_CSV_FR.zip"
SORTIE = RACINE / "data" / "processed" / "taux-emploi-age-sexe-2025.csv"
FICHIER_DONNEES = "DD_EEC_ANNUEL_2025_data.csv"

# Dimensions fixées à « total » (_T) pour ne garder que l'âge et le sexe.
DIMENSIONS_TOTAL = ["EMPFORM", "PCS", "EDUC", "IMMI", "WKTIME", "ACTIVITY", "UNDEREMP", "UNEMPDUR", "COMPOHALO"]
EMPLOYE = "1_BIT"   # statut « en emploi » au sens du BIT


def lire(zip_path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path) as z:
        d = pd.read_csv(z.open(FICHIER_DONNEES), sep=";", dtype=str)
    d["OBS_VALUE"] = pd.to_numeric(d["OBS_VALUE"])
    for col in DIMENSIONS_TOTAL:
        d = d[d[col] == "_T"]
    return d


def construire(d: pd.DataFrame) -> pd.DataFrame:
    pop = d[(d.EEC_MEASURE == "POP") & (d.EMPSTA == "_T")].pivot(index="AGE", columns="SEX", values="OBS_VALUE")
    part = d[(d.EEC_MEASURE == "PT_EMPSTA_IN_POP") & (d.EMPSTA == EMPLOYE)].pivot(
        index="AGE", columns="SEX", values="OBS_VALUE")
    lignes = []
    for age in part.index:
        if age not in pop.index or age == "_T":
            continue
        for code, nom in (("F", "F"), ("M", "H")):
            p_sexe, p_tot = pop.loc[age, code], pop.loc[age, "_T"]
            part_sexe = part.loc[age, code]       # emploi du sexe, rapporté à la population des DEUX sexes
            if pd.isna(p_sexe) or pd.isna(p_tot) or pd.isna(part_sexe):
                continue
            e = part_sexe / 100.0 / (p_sexe / p_tot)   # taux d'emploi du sexe, rapporté à sa propre population
            lignes.append((age, nom, 100 * e, p_sexe, part_sexe))
    return pd.DataFrame(lignes, columns=["age", "sexe", "taux_emploi_pct", "population_milliers",
                                         "part_emploi_dans_pop_totale_pct"])


if __name__ == "__main__":
    chemin = Path(sys.argv[1]) if len(sys.argv) > 1 else ZIP_PAR_DEFAUT
    if not chemin.exists():
        sys.exit(f"Fichier introuvable : {chemin}")
    table = construire(lire(chemin))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(SORTIE, index=False, float_format="%.4f")
    print(f"{len(table)} lignes écrites dans {SORTIE}")
    print(table[table.age.isin(["Y62", "Y63", "Y64", "Y65T69"])].to_string(index=False))
