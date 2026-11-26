"""Phase 3 : extrait de l'EACR (Drees) les trois tables utilisées par le moteur financier.

Usage (depuis la racine du dépôt) :
    python scripts/build_eacr_tables.py [chemin_du_fichier_EACR.xlsx] [année]

Lit le classeur de la Drees (24 Mo, environ 40 secondes) et écrit, dans data/processed/ (ignoré par Git) :
- eacr-stock-<année>.csv                 stock de retraités de droit direct par sexe et âge (effectifs, m1) ;
- eacr-nouveaux-liquidants-<année>.csv   nouveaux liquidants de droit direct de l'année (effectifs, m1) ;
- eacr-age-conjoncturel-<année>.csv      âge conjoncturel de départ par caisse et sexe.

Sélection (fiche 10, docs/donnees.md) : onglet C-Droits_directs, « Tous régimes » (modèle Ancetre),
résidence « Ensemble », naissance « Ensemble », droit direct (`ddir`) pour le stock, nouveaux liquidants
(`nl_ddir`) pour les flux. `m1` est l'avantage principal moyen de droit direct perçu en décembre.
"""
import sys
from pathlib import Path

import openpyxl
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
DEFAUT = RACINE / "data" / "raw" / "62 EACR diffusée Part 1 - version du 26 mai 2026.xlsx"
SORTIE = RACINE / "data" / "processed"


def lire_onglet(classeur, nom: str) -> pd.DataFrame:
    ws = classeur[nom]
    ws.reset_dimensions()          # le classeur déclare mal sa taille : sans cet appel, une seule ligne est lue
    lignes = list(ws.iter_rows(values_only=True))
    return pd.DataFrame(lignes[1:], columns=lignes[0])


def extraire(c: pd.DataFrame, annee: int, champ: str) -> pd.DataFrame:
    t = c[(c["Année"].astype(str) == str(annee)) & (c.Caisse == "Tous régimes") & (c.Resid == "Ensemble")
          & (c.Naiss == "Ensemble") & (c.Champ == champ) & (c.Liq == "Ensemble")]
    t = t[["Sexe", "Age", "effectifs", "m1"]].rename(columns={"Sexe": "sexe", "Age": "age"})
    t["sexe"] = t["sexe"].map({"Femmes": "F", "Hommes": "H", "Ensemble": "T"})
    return t.reset_index(drop=True)


if __name__ == "__main__":
    chemin = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAUT
    annee = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
    if not chemin.exists():
        sys.exit(f"Fichier introuvable : {chemin}")
    classeur = openpyxl.load_workbook(chemin, read_only=True)
    SORTIE.mkdir(parents=True, exist_ok=True)

    droits = lire_onglet(classeur, "C-Droits_directs")
    stock = extraire(droits, annee, "ddir")
    flux = extraire(droits, annee, "nl_ddir")
    stock.to_csv(SORTIE / f"eacr-stock-{annee}.csv", index=False)
    flux.to_csv(SORTIE / f"eacr-nouveaux-liquidants-{annee}.csv", index=False)

    ac = lire_onglet(classeur, "A-Age_conjoncturel")
    ac = ac[ac["Année"].astype(str) == str(annee)][["Caisse", "Sexe", "ageconj"]]
    ac["Sexe"] = ac["Sexe"].map({"Femmes": "F", "Hommes": "H", "Ensemble": "T"})
    ac.rename(columns={"Caisse": "caisse", "Sexe": "sexe"}).to_csv(
        SORTIE / f"eacr-age-conjoncturel-{annee}.csv", index=False)

    for nom, t in (("stock", stock), ("nouveaux liquidants", flux)):
        ind = t[t.age.str.fullmatch(r"\d+")]
        print(f"{nom} : {len(t)} lignes ; effectifs aux âges individuels F {ind[ind.sexe == 'F'].effectifs.sum():,.0f}"
              f" H {ind[ind.sexe == 'H'].effectifs.sum():,.0f} ; ligne Ensemble "
              f"{t[(t.sexe == 'T') & (t.age == 'Ensemble')].effectifs.sum():,.0f}")
