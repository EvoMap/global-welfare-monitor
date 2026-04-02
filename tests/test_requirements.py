"""Verify that all imports used in src/ are satisfiable from requirements.txt."""

import importlib


REQUIRED_PACKAGES = [
    ("dotenv", "python-dotenv"),
    ("wbgapi", "wbgapi"),
    ("fastapi", "fastapi"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("requests", "requests"),
    ("feedparser", "feedparser"),
    ("sklearn", "scikit-learn"),
]


def test_critical_packages_importable():
    """All packages referenced in src/ must be installable."""
    for module_name, pkg_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            raise AssertionError(
                f"Package '{pkg_name}' (import {module_name}) is missing. "
                f"It must be listed in requirements.txt."
            )
