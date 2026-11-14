"""Save, once, the census tract shapes the project maps are drawn on: GEOID and polygon only.

    python scripts/extract_tracts.py PATH/TO/tracts.shp            # first run
    python scripts/extract_tracts.py PATH/TO/tracts.shp --force    # replace the saved file

Input: a 2023 census tract layer for the five New York City counties, clipped
to the shoreline (U.S. Census Bureau TIGER/Line 2023 tracts; any format
GeoPandas reads). Every column except GEOID is dropped, so no data travels
with the shapes: what is saved is public geometry, and it is committed.

Writes the shapefile scripts/figures/data/geometry/nyc_tracts_2023.shp (with
its .shx, .dbf, .prj and .cpg) in WGS 84. Coordinates are kept exactly as
read: rounding them would open slivers between neighbouring tracts. The
figure builder turns the shapes into drawing paths (stage `geometry` of
scripts/build_figures.py).

Packages: geopandas and shapely, both installed with libpysal from
scripts/requirements-figures.txt.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely

logger = logging.getLogger("extract_tracts")

# ==========================================================================
# [Config] What to keep
# ==========================================================================
STATE = "36"  # New York
COUNTIES = {"005", "047", "061", "081", "085"}  # Bronx, Brooklyn, Manhattan, Queens, Staten Island
# A tract's polygon area over its official land area: near 1 when the layer is
# clipped to the shoreline, far above 1 when it still covers water.
LAND_RATIO = (0.97, 1.03)

REPO_ROOT = Path(__file__).resolve().parents[1]
ACS_CSV = REPO_ROOT / "scripts" / "figures" / "data" / "acs" / "nyc_tracts_acs5_2023.csv"
OUT = REPO_ROOT / "scripts" / "figures" / "data" / "geometry" / "nyc_tracts_2023.shp"


def load(path: Path) -> gpd.GeoDataFrame:
    """Read the layer, keep New York City's tracts, and check them against the ACS extract."""
    layer = gpd.read_file(path)
    if "GEOID" not in layer.columns:
        raise SystemExit(f"{path} has no GEOID column.")
    if layer.crs is None:
        raise SystemExit(f"{path} has no coordinate system.")
    layer["GEOID"] = layer["GEOID"].astype(str)
    city = layer[layer["GEOID"].str[:2].eq(STATE) & layer["GEOID"].str[2:5].isin(COUNTIES)]
    if city["GEOID"].str.len().ne(11).any() or city["GEOID"].duplicated().any():
        raise SystemExit("GEOIDs must be 11 digits and unique.")
    if not city.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise SystemExit("every tract must be a polygon.")

    if "ALAND" in city.columns:
        area = city.to_crs("ESRI:102003").area / pd.to_numeric(city["ALAND"]).where(lambda a: a > 0)
        median = float(area.median())
        if not LAND_RATIO[0] <= median <= LAND_RATIO[1]:
            raise SystemExit(f"polygon area is {median:.2f} times the land area: the layer is not clipped to the shoreline.")
        logger.info("  > polygon area / land area, median: %.3f (clipped to the shoreline)", median)

    acs = pd.read_csv(ACS_CSV, dtype={"geoid": str}, usecols=["geoid", "total_population"])
    missing = acs[~acs["geoid"].isin(city["GEOID"])]
    if missing["total_population"].gt(0).any():
        raise SystemExit(f"tracts with residents have no shape: {missing['geoid'].tolist()}")
    extra = sorted(set(city["GEOID"]) - set(acs["geoid"]))
    if extra:
        raise SystemExit(f"shapes with no ACS row: {extra[:5]}")
    logger.info("  > %d tracts; %d ACS tracts without a shape, none with residents", len(city), len(missing))
    return city[["GEOID", "geometry"]].to_crs("EPSG:4326").sort_values("GEOID")


def write(tracts: gpd.GeoDataFrame, path: Path) -> None:
    """Write the shapes with GEOID as the only attribute, after checking they still tile the city."""
    shapes = tracts.geometry.values
    if not shapely.is_valid(shapes).all():
        raise SystemExit("a tract shape is invalid.")
    if not shapely.coverage_is_valid(shapes):
        raise SystemExit("neighbouring tracts overlap or leave gaps.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tracts.reset_index(drop=True).to_file(path, driver="ESRI Shapefile", encoding="utf-8")
    size = sum(part.stat().st_size for part in path.parent.glob(f"{path.stem}.*"))
    logger.info("  > wrote %s and its sidecar files (%d kB)", path.relative_to(REPO_ROOT), size // 1000)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("layer", type=Path, help="tract layer to read (shapefile, GeoPackage, GeoJSON)")
    parser.add_argument("--force", action="store_true", help="replace the saved file")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if OUT.exists() and not args.force:
        logger.info("  > %s exists; pass --force to replace it", OUT.relative_to(REPO_ROOT))
        return 0
    write(load(args.layer), OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
