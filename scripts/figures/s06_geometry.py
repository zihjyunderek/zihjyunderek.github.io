"""Turn the tract shapes into the SVG paths the maps draw: projected, simplified, in whole units.

Reads the GEOID-only shapefile saved by scripts/extract_tracts.py and writes
src/data/figures/geometry/nyc_tracts.json: the drawing's width and height and
one SVG path per GEOID. A map figure looks its shapes up there by GEOID
(src/lib/figures/map.ts), so the figure CSVs carry a GEOID and no coordinates.

Simplification keeps the tracts a coverage (shapely.coverage_simplify): two
neighbours keep one shared edge, so no gap or overlap opens between them.
"""

from __future__ import annotations

import json
import logging
import math

import geopandas as gpd
import numpy as np
import shapely

from figures import config

logger = logging.getLogger(__name__)


def project(shapes: np.ndarray) -> tuple[np.ndarray, int]:
    """Place the shapes in drawing units: equirectangular, north up, `MAP_WIDTH` wide."""
    west, south, east, north = shapely.total_bounds(shapes)
    # at city scale, shrinking longitude by cos(latitude) keeps shapes true
    squeeze = math.cos(math.radians((south + north) / 2))
    pad = config.MAP_PAD
    scale = (config.MAP_WIDTH - 2 * pad) / ((east - west) * squeeze)
    height = math.ceil((north - south) * scale + 2 * pad)
    placed = shapely.transform(
        shapes, lambda xy: np.column_stack([pad + (xy[:, 0] - west) * squeeze * scale, pad + (north - xy[:, 1]) * scale])
    )
    return placed, height


def numbers(values: np.ndarray) -> str:
    """Join whole numbers as an SVG path allows: a minus sign doubles as the separator."""
    return "".join(f"{v}" if i == 0 or v < 0 else f" {v}" for i, v in enumerate(values.tolist()))


def path(shape: shapely.Geometry) -> str:
    """Write a polygon as an SVG path: whole units, relative moves, each ring closed."""
    rings = []
    for polygon in getattr(shape, "geoms", [shape]):
        for ring in (polygon.exterior, *polygon.interiors):
            # round the corners themselves, then take differences: neighbours share
            # corners, so they still meet exactly after rounding
            corners = np.rint(np.asarray(ring.coords)[:-1]).astype(int)
            corners = corners[np.r_[True, np.any(np.diff(corners, axis=0) != 0, axis=1)]]
            if len(corners) < 3:
                continue  # a ring smaller than one unit
            rings.append(f"M{numbers(corners[0])}l{numbers(np.diff(corners, axis=0).ravel())}z")
    return "".join(rings)


def run() -> None:
    """Write the drawing paths for every tract."""
    tracts = gpd.read_file(config.TRACT_SHAPES).sort_values("GEOID")
    if tracts.crs is None or tracts.crs.to_epsg() != 4326:
        raise ValueError(f"{config.TRACT_SHAPES.name} must be in WGS 84 (EPSG:4326).")
    placed, height = project(np.asarray(tracts.geometry))
    simple = shapely.coverage_simplify(placed, config.MAP_TOLERANCE)
    places = {geoid: path(shape) for geoid, shape in zip(tracts["GEOID"], simple)}
    empty = [geoid for geoid, d in places.items() if not d]
    if empty:
        raise ValueError(f"tracts smaller than one drawing unit: {empty[:5]}")
    logger.info("  > %d tracts, %d corners after simplification (from %d), drawing %d x %d",
                len(places), int(shapely.get_num_coordinates(simple).sum()),
                int(shapely.get_num_coordinates(placed).sum()), config.MAP_WIDTH, height)

    out = config.MAP_SHAPES
    out.parent.mkdir(parents=True, exist_ok=True)
    head = {"source": config.MAP_SHAPES_SOURCE, "width": config.MAP_WIDTH, "height": height}
    lines = [f"{json.dumps(geoid)}:{json.dumps(d)}" for geoid, d in places.items()]
    body = json.dumps(head, separators=(",", ":"))[:-1] + ',"places":{\n' + ",\n".join(lines) + "\n}}\n"
    out.write_text(body, encoding="utf-8")
    logger.info("  > wrote %s (%d kB)", out.relative_to(config.REPO_ROOT), out.stat().st_size // 1000)
