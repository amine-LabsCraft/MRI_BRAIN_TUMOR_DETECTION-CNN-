"""
Auto-discovery registry for analyses.

Each analysis module (``analyses/figXX_*.py``) must expose:

    NAME         : str   — output filename stem (e.g. "01_class_distribution")
    TITLE        : str   — human-readable short title
    DESCRIPTION  : str   — one-line description
    CATEGORY     : str   — one of {"overview", "image", "training", "evaluation", "errors"}
    REQUIRES     : list  — sources needed: any of {"data", "logs", "results"}
    ORDER        : int   — sort order for run/list

    def run() -> dict:
        '''Compute, plot, save → return a dict for summary.json.'''

The registry walks ``analyses/`` and instantiates a ``RegisteredAnalysis`` per
module. Missing source files → analysis is reported as ``[skipped]`` rather
than failing.
"""
from __future__ import annotations

import importlib
import importlib.util
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from .config import DATA_DIR, LOGS_DIR, RESULTS_DIR
from .plotting import save_data, set_current_category


_ANALYSES_PKG = "analyses"


@dataclass
class RegisteredAnalysis:
    name: str
    title: str
    description: str
    category: str
    requires: list[str]
    order: int
    run: Callable[[], dict]
    module_path: Path

    def is_runnable(self) -> tuple[bool, str | None]:
        """Check that all required source folders/files are available."""
        for req in self.requires:
            if req == "data" and not DATA_DIR.exists():
                return False, f"missing data folder: {DATA_DIR}"
            if req == "logs":
                if not LOGS_DIR.exists() or not list(LOGS_DIR.glob("training_history_*.csv")):
                    return False, "missing training_history_*.csv in logs/"
            if req == "results":
                if not (RESULTS_DIR / "test_results.csv").exists():
                    return False, "missing results/test_results.csv"
        return True, None


# ─── Discovery ────────────────────────────────────────────────────────────────
def discover() -> list[RegisteredAnalysis]:
    """Scan analyses/ for figXX_*.py modules and register them."""
    analyses_dir = Path(__file__).resolve().parent.parent / "analyses"
    if not analyses_dir.is_dir():
        return []

    items: list[RegisteredAnalysis] = []
    for py in sorted(analyses_dir.glob("fig*.py")):
        if py.name.startswith("_"):
            continue
        mod_name = f"{_ANALYSES_PKG}.{py.stem}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ Failed to import {mod_name}: {e}")
            continue

        # Collect required attributes; skip module if interface incomplete
        try:
            item = RegisteredAnalysis(
                name        = mod.NAME,
                title       = mod.TITLE,
                description = mod.DESCRIPTION,
                category    = getattr(mod, "CATEGORY", "misc"),
                requires    = list(getattr(mod, "REQUIRES", [])),
                order       = int(getattr(mod, "ORDER", 999)),
                run         = mod.run,
                module_path = py,
            )
        except AttributeError as e:
            print(f"  ⚠ {mod_name} skipped — missing attribute ({e})")
            continue
        items.append(item)

    items.sort(key=lambda x: x.order)
    return items


# ─── Execution ────────────────────────────────────────────────────────────────
def run_one(item: RegisteredAnalysis, verbose: bool = True) -> dict | None:
    """Execute a single analysis. Returns its data dict (or None if skipped)."""
    ok, why = item.is_runnable()
    if not ok:
        if verbose:
            print(f"  [skip] {item.name:38s}  ({why})")
        return None

    if verbose:
        print(f"  [run ] {item.name:38s}  {item.title}")

    t0 = time.perf_counter()
    set_current_category(item.category)
    try:
        data = item.run() or {}
    except Exception as e:  # noqa: BLE001
        print(f"  [FAIL] {item.name}: {e}")
        traceback.print_exc()
        return None
    finally:
        set_current_category(None)
    elapsed = time.perf_counter() - t0

    # Save per-analysis JSON (force category subfolder)
    save_data(item.name, {
        "title":       item.title,
        "category":    item.category,
        "elapsed_sec": round(elapsed, 3),
        "data":        data,
    }, category=item.category)

    if verbose:
        print(f"         ↳ ✓ {elapsed:.2f}s")

    return data


def run_many(items: Iterable[RegisteredAnalysis]) -> dict[str, dict | None]:
    """Run several analyses sequentially and collect results."""
    results: dict[str, dict | None] = {}
    for item in items:
        results[item.name] = run_one(item)
    return results
