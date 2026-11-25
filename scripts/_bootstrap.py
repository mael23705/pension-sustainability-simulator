"""Ajoute src/ au chemin de Python pour que les scripts tournent sans installation."""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))
