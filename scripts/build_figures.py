"""Rebuild the CSVs behind the site's figures.

    python scripts/build_figures.py                # every stage
    python scripts/build_figures.py mgwr index     # only the stages named

Stages read the public ACS extract saved by scripts/fetch_acs.py and the tract
shapes saved by scripts/extract_tracts.py (no network, no key), and write to
src/data/figures/<project>/ and, for the map shapes, src/data/figures/geometry/.
The site then draws the figures from those files at build time. Settings:
scripts/figures/config.py.
Packages: pip install -r scripts/requirements-figures.txt
"""

from __future__ import annotations

import argparse
import importlib
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# stage name -> module under scripts/figures/
STAGES = {
    "geometry": "figures.s06_geometry",
    "mgwr": "figures.s02_mgwr",
    "archetypes": "figures.s03_archetypes",
    "index": "figures.s04_exclusion_index",
    "satisfaction": "figures.s05_satisfaction",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stages", nargs="*", choices=[*STAGES, []], help="stages to run; default is all")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    for name in args.stages or STAGES:
        started = time.perf_counter()
        logging.info("\n--- %s ---", name)
        importlib.import_module(STAGES[name]).run()
        logging.info("  > done in %.1fs", time.perf_counter() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
