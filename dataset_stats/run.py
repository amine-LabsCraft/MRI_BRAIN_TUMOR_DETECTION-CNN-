"""
═══════════════════════════════════════════════════════════════════════════════
 BrainScan AI — Dataset Statistics & Figures Generator (modular)
═══════════════════════════════════════════════════════════════════════════════

Usage examples
--------------
    python run.py                       # run all analyses
    python run.py --list                # list available analyses & exit
    python run.py --only 01,03,07       # run a subset (by id)
    python run.py --except 06           # run all except some
    python run.py --filter training     # name/title contains substring
    python run.py --category evaluation # one of: overview, image, training,
                                        #   evaluation, errors, misc

Architecture
------------
    core/         shared infrastructure (config, data loading, plotting, registry)
    analyses/     one file = one analysis (figXX_*.py); auto-discovered
    outputs/      figures/  → *.png
                  data/     → per-analysis JSON
                  summary.json → master summary

Adding a new analysis
---------------------
1. Drop a new file in `analyses/` named `figXX_<slug>.py`
2. Expose: NAME, TITLE, DESCRIPTION, CATEGORY, REQUIRES, ORDER, def run()
3. That's it — registry picks it up next time `run.py` is invoked.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Make `core` and `analyses` importable when run.py is launched directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import discover, run_one, setup_matplotlib  # noqa: E402
from core.config import SUMMARY_JSON                  # noqa: E402


# ─── Selection helpers ────────────────────────────────────────────────────────
def parse_ids(spec: str | None) -> set[str] | None:
    """Parse "01,03,07" → {"01", "03", "07"}. None or empty → None (= all)."""
    if not spec:
        return None
    return {p.strip().zfill(2) for p in spec.split(",") if p.strip()}


def filter_items(items, only=None, exclude=None, name_filter=None, category=None):
    out = []
    for it in items:
        prefix = it.name.split("_", 1)[0]  # "01" from "01_class_distribution"
        if only      and prefix not in only:                   continue
        if exclude   and prefix in exclude:                    continue
        if name_filter and name_filter.lower() not in (it.name + " " + it.title).lower(): continue
        if category  and it.category != category:              continue
        out.append(it)
    return out


# ─── List rendering ───────────────────────────────────────────────────────────
def render_list(items) -> None:
    print(f"\n{'═' * 80}")
    print(f"  Available analyses ({len(items)} registered)")
    print(f"{'═' * 80}")
    cur_category = None
    for it in items:
        if it.category != cur_category:
            cur_category = it.category
            print(f"\n  ── {cur_category.upper()} ──")
        ok, why = it.is_runnable()
        status = "  ✓ " if ok else "  ✗ "
        prefix = it.name.split("_", 1)[0]
        print(f"  {status}{prefix}  {it.title:34s}  [{','.join(it.requires) or 'none':<22s}]"
              + ("" if ok else f"  ⚠ {why}"))
    print()


# ─── Banner ───────────────────────────────────────────────────────────────────
def banner(title: str) -> None:
    print(f"\n{'═' * 80}\n  {title}\n{'═' * 80}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate dataset statistics & figures (modular).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--list",     action="store_true", help="List available analyses and exit")
    ap.add_argument("--only",     type=str, default=None, help="Comma-separated IDs (e.g. 01,03,07)")
    ap.add_argument("--except",   dest="exclude", type=str, default=None, help="IDs to skip")
    ap.add_argument("--filter",   type=str, default=None, help="Substring match against name/title")
    ap.add_argument("--category", type=str, default=None,
                    choices=["overview", "image", "training", "evaluation", "errors", "misc"])
    args = ap.parse_args()

    setup_matplotlib()

    items = discover()
    if not items:
        print("✗ No analyses discovered in analyses/.", file=sys.stderr)
        return 1

    selected = filter_items(items,
                            only=parse_ids(args.only),
                            exclude=parse_ids(args.exclude),
                            name_filter=args.filter,
                            category=args.category)

    if args.list:
        render_list(items)
        return 0

    if not selected:
        print("✗ No analyses match the given filters.")
        render_list(items)
        return 1

    banner(f"Running {len(selected)} / {len(items)} analyses")
    t0 = time.perf_counter()
    summary: dict = {
        "version":       "2.0.0",
        "generated_by":  "dataset_stats/run.py",
        "n_run":         len(selected),
        "n_total":       len(items),
        "analyses":      {},
    }

    for it in selected:
        data = run_one(it)
        summary["analyses"][it.name] = {
            "title":    it.title,
            "category": it.category,
            "requires": it.requires,
            "data":     data,
        }

    elapsed = time.perf_counter() - t0
    summary["elapsed_sec"] = round(elapsed, 2)

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    banner(f"✅ Done — {len(selected)} analyses in {elapsed:.2f}s")
    print(f"  Figures        → {SUMMARY_JSON.parent / 'figures'}")
    print(f"  Per-analysis   → {SUMMARY_JSON.parent / 'data'}")
    print(f"  Summary JSON   → {SUMMARY_JSON}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        raise SystemExit(130)
