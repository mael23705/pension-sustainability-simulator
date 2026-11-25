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
]

manquants = 0
for nom in attendus:
    chemin = dossier / nom
    if chemin.exists():
        print(f"présent   {nom}  ({chemin.stat().st_size / 1e6:.1f} Mo)")
    else:
        print(f"manquant  {nom}  (attendu dans {dossier})")
        manquants += 1

sys.exit(1 if manquants else 0)
