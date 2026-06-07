"""
Tests for the dataset_stats package — registry auto-discovery and
runnable analyses with no external requirements.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "dataset_stats"))


@pytest.fixture(scope="module")
def registry():
    from core import discover  # type: ignore[import-not-found]
    return discover()


def test_registry_discovers_all_analyses(registry):
    # Auto-discovers any figXX_*.py file in analyses/
    # Lower bound = 22 (current count); upper bound = 100 (sanity)
    assert 22 <= len(registry) <= 100


def test_all_analyses_have_required_attributes(registry):
    for it in registry:
        assert it.name and it.title
        assert it.category in {"overview", "image", "training", "evaluation", "errors", "misc"}
        assert isinstance(it.requires, list)
        assert callable(it.run)


def test_analyses_sorted_by_order(registry):
    orders = [it.order for it in registry]
    assert orders == sorted(orders)


def test_no_dependency_analysis_runs():
    """fig04_image_properties has no external deps — must run."""
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT / "dataset_stats"))
    mod = importlib.import_module("analyses.fig04_image_properties")
    result = mod.run()
    assert isinstance(result, dict)
    assert len(result) > 0
