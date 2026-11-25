"""Fixtures communes aux tests."""
from pathlib import Path

import pytest

from config import load_config

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def cfg() -> dict:
    return load_config(ROOT / "config" / "assumptions.yaml")
