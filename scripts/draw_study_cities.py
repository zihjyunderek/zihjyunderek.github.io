"""Draw, once, the CDI-Milestone illustration: the 15 study cities, each tract shaded by its size.

    python scripts/draw_study_cities.py PATH/TO/shapefiles

Input: one census tract layer per city, U.S. Census Bureau TIGER/Line 2023
tracts, found as <folder>/<City>/census_boundary/*.shp.
Only the shapes, and the land area to drop water-only tracts, are read.
Shading uses each tract's own area (smaller tracts are darker, which in a
city mostly means denser), so the drawing carries no survey, client or
attribute data. Tracts of one size class are merged into
one shape per city, which keeps the drawing light.

Writes:
  * src/data/figures/geometry/study_cities.json      the 15 cities in a 5 x 3 grid, in drawing units
  * src/data/figures/cdi-milestone/study_cities.csv  each shape's name ("Atlanta: Smallest fifth") and class

The raw layers are about 30 MB, so they are not committed: this drawing is an
illustration, not data a figure measures. Settings are the constants below.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figures.s06_geometry import path  # noqa: E402  (same path writer as the NYC maps)

logger = logging.getLogger("draw_study_cities")

# ==========================================================================
# [Config] The drawing
# ==========================================================================
# folder name -> name in the caption, in reading order (alphabetical by caption name)
CITIES = {
    "Atlanta": "Atlanta", "Austin": "Austin", "Boston": "Boston", "Chicago": "Chicago", "Dallas": "Dallas",
    "Denver": "Denver", "Houston": "Houston", "LA": "Los Angeles", "Miami": "Miami", "NYC": "New York",
    "Philadelphia": "Philadelphia", "SanDiego": "San Diego", "SF": "San Francisco", "Seattle": "Seattle",
    "DC": "Washington",
}
COLUMNS = 5
CELL = 180       # drawing units per city, square; cities are fitted, not to scale
GAP = 15         # between cells
TOLERANCE = 1.0  # drawing units; neighbours keep shared edges (coverage simplification)
CLASSES = ["Smallest fifth", "Second fifth", "Middle fifth", "Fourth fifth", "Largest fifth"]
# Islands far offshore (the Farallones for San Francisco) would shrink a city
# to a corner of its square: parts farther from the centre than this many
# times the reach of the city's own tracts are left out.
OUTLYING = 1.5

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_SHAPES = REPO_ROOT / "src" / "data" / "figures" / "geometry" / "study_cities.json"
OUT_CSV = REPO_ROOT / "src" / "data" / "figures" / "cdi-milestone" / "study_cities.csv"


def city(folder: Path) -> gpd.GeoDataFrame:
    """Read one city's land tracts, GEOID and shape only, in a local metric projection, without far islands."""
    layers = sorted(folder.glob("census_boundary/*.shp"))
    if len(layers) != 1:
        raise SystemExit(f"expected one tract layer in {folder}/census_boundary, found {len(layers)}.")
    layer = gpd.read_file(layers[0])
    tracts = layer.loc[pd.to_numeric(layer["ALAND"]) > 0, ["GEOID", "geometry"]]  # water-only tracts out
    tracts = tracts.to_crs(tracts.estimate_utm_crs()).reset_index(drop=True)
    points = tracts.representative_point()
    centre = shapely.Point(points.x.median(), points.y.median())
    reach = OUTLYING * points.distance(centre).quantile(0.99)
    parts = tracts.explode(index_parts=False)
    parts = parts[parts.centroid.distance(centre) <= reach]
    return parts.dissolve("GEOID").reset_index()[["GEOID", "geometry"]]


def place(tracts: gpd.GeoDataFrame, column: int, row: int) -> np.ndarray:
    """Fit one city into its grid cell, north up, centred."""
    west, south, east, north = tracts.total_bounds
    scale = CELL / max(east - west, north - south)
    x0 = column * (CELL + GAP) + (CELL - (east - west) * scale) / 2
    y0 = row * (CELL + GAP) + (CELL - (north - south) * scale) / 2
    return shapely.transform(
        np.asarray(tracts.geometry), lambda xy: np.column_stack([x0 + (xy[:, 0] - west) * scale, y0 + (north - xy[:, 1]) * scale])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path, help="folder holding <City>/census_boundary/*.shp")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    places, rows = {}, []
    for i, (name, label) in enumerate(CITIES.items()):
        tracts = city(args.folder / name)
        # size classes within the city: area quintiles, smallest first
        size = pd.qcut(tracts.area.rank(method="first"), len(CLASSES), labels=CLASSES).astype(str)
        merged = gpd.GeoDataFrame({"size": size}, geometry=place(tracts, i % COLUMNS, i // COLUMNS)).dissolve("size")
        for cls, shape in zip(merged.index, shapely.coverage_simplify(np.asarray(merged.geometry), TOLERANCE)):
            places[f"{label}: {cls}"] = path(shape)
            rows.append({"place": f"{label}: {cls}", "size": cls})
        logger.info("  > %-14s %5d tracts", label, len(tracts))

    width = COLUMNS * CELL + (COLUMNS - 1) * GAP
    height = math.ceil(len(CITIES) / COLUMNS) * (CELL + GAP) - GAP
    OUT_SHAPES.parent.mkdir(parents=True, exist_ok=True)
    head = {"source": "U.S. Census Bureau, TIGER/Line 2023 census tracts, water-only tracts and far islands left out", "width": width, "height": height}
    lines = [f"{json.dumps(geoid)}:{json.dumps(d)}" for geoid, d in places.items()]
    OUT_SHAPES.write_text(json.dumps(head, separators=(",", ":"))[:-1] + ',"places":{\n' + ",\n".join(lines) + "\n}}\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, lineterminator="\n")
    logger.info("  > wrote %s (%d kB) and %s, %d shapes", OUT_SHAPES.relative_to(REPO_ROOT),
                OUT_SHAPES.stat().st_size // 1000, OUT_CSV.relative_to(REPO_ROOT), len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
