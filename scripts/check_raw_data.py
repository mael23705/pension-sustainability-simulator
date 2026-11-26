"""Étape 2 : vérifie la présence des fichiers bruts attendus dans data/raw/.

Usage (depuis la racine du dépôt) :  python scripts/check_raw_data.py
Pas de téléchargement automatique : les fichiers sont déposés à la main dans data/raw/.
Code de sortie 0 si tout est présent, 1 sinon.
"""
import sys

import _bootstrap  # noqa: F401  (ajoute src/ au chemin)
from config import get_param, load_config

cfg = load_config(_bootstrap.RACINE / "config" / "assumptions.yaml")
dossier = _bootstrap.RACINE / get_param(cfg, "data_files.raw_dir")

attendus = [
    get_param(cfg, "data_files.insee_population_file"),
    get_param(cfg, "data_files.insee_projection_file"),
    get_param(cfg, "data_files.eec_zip_file"),     # phase 3 : enquête Emploi 2025 (build_employment_table.py)
    get_param(cfg, "data_files.eacr_xlsx_file"),   # phase 3 : EACR de la Drees (build_eacr_tables.py)
]

manquants = 0
for nom in attendus:
    chemin = dossier / nom
    if chemin.exists():
        print(f"présent   {nom}  ({chemin.stat().st_size / 1e6:.1f} Mo)")
    else:
        print(f"manquant  {nom}  (attendu dans {dossier})")
        manquants += 1

# Tables dérivées (phase 3) : reconstruites par les scripts build_*, jamais téléchargées.
derives = [get_param(cfg, f"data_files.{k}") for k in ("employment_table", "eacr_stock_table", "eacr_new_retirees_table", "eacr_age_table")]
for nom in derives:
    chemin = _bootstrap.RACINE / get_param(cfg, "data_files.processed_dir") / nom
    print(("présent   " if chemin.exists() else "à générer  ") + f"{nom}  (data/processed/)")

sys.exit(1 if manquants else 0)
