"""Lecture de la configuration : pas de valeur par défaut silencieuse."""
import pytest

from config import ConfigError, get_param, load_config


def test_parametre_nul_leve_une_erreur_claire(cfg):
    with pytest.raises(ConfigError, match="nul"):
        get_param(cfg, "finance.contribution_rate_tau0")


def test_parametre_absent_leve_une_erreur_claire(cfg):
    with pytest.raises(ConfigError, match="absent"):
        get_param(cfg, "demography.parametre_inexistant")


def test_valeur_lue_dans_le_yaml(cfg):
    assert get_param(cfg, "demography.entry_age_a0") == 20
    assert get_param(cfg, "demography.open_class_age") == 100


def test_fichier_introuvable(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "absent.yaml")
