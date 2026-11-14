"""Tract indicators derived from the public ACS extract.

The extract holds raw counts and medians. This stage turns them into the
rates and shares the analyses use, keeps residential tracts only, and adds
planar coordinates in kilometres so distances are plain Euclidean.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import config

logger = logging.getLogger(__name__)

KM_PER_DEGREE = 111.32


def _share(part: pd.Series, whole: pd.Series) -> pd.Series:
    """Return part / whole in percent, blank where the universe is empty."""
    return (100.0 * part / whole.where(whole > 0)).astype(float)


def load_tracts() -> pd.DataFrame:
    """Return one row per residential tract: identifiers, coordinates, indicators."""
    if not config.ACS_CSV.is_file():
        raise FileNotFoundError(f"{config.ACS_CSV} is missing. Run: python scripts/fetch_acs.py")
    raw = pd.read_csv(config.ACS_CSV, dtype={"geoid": str})

    tracts = raw[["geoid", "borough", "tract_name", "lat", "lon"]].copy()
    # equirectangular around the city's mean latitude: accurate to a few metres at this extent
    squeeze = np.cos(np.radians(raw["lat"].mean()))
    tracts["x_km"] = (raw["lon"] - raw["lon"].mean()) * squeeze * KM_PER_DEGREE
    tracts["y_km"] = (raw["lat"] - raw["lat"].mean()) * KM_PER_DEGREE

    tracts["population"] = raw["total_population"]
    tracts["households"] = raw["households"]
    tracts["density"] = raw["total_population"] / raw["land_sqkm"].where(raw["land_sqkm"] > 0)
    for column in ("median_household_income", "median_gross_rent", "median_rent_pct_of_income",
                   "median_home_value", "median_age", "median_rooms", "gini_index"):
        tracts[column] = raw[column]

    college = raw[["bachelors_degree", "masters_degree", "professional_degree", "doctorate_degree"]].sum(axis=1)
    crowded = raw[[c for c in raw.columns if "_crowded_" in c]].sum(axis=1)
    tracts["college_share"] = _share(college, raw["population_25_plus"])
    tracts["poverty_rate"] = _share(raw["below_poverty"], raw["poverty_universe"])
    tracts["unemployment_rate"] = _share(raw["unemployed"], raw["civilian_labor_force"])
    tracts["renter_share"] = _share(raw["renter_occupied_units"], raw["occupied_units"])
    tracts["vacancy_rate"] = _share(raw["vacant_units"], raw["housing_units"])
    tracts["prewar_share"] = _share(raw["units_built_1939_or_earlier"], raw["units_by_year_built"])
    tracts["new_housing_share"] = _share(
        raw["units_built_2010_to_2019"] + raw["units_built_2020_or_later"], raw["units_by_year_built"])
    tracts["transit_share"] = _share(raw["commute_public_transit"], raw["workers"])
    tracts["walk_bike_share"] = _share(raw["commute_walked"] + raw["commute_bicycle"], raw["workers"])
    tracts["work_from_home_share"] = _share(raw["worked_from_home"], raw["workers"])
    tracts["no_vehicle_share"] = _share(raw["households_no_vehicle"], raw["households"])
    tracts["no_internet_share"] = _share(raw["households_no_internet"], raw["households_internet_universe"])
    tracts["foreign_born_share"] = _share(raw["foreign_born"], raw["nativity_universe"])
    tracts["crowded_share"] = _share(crowded, raw["occupants_per_room_universe"])

    residential = (tracts["population"] >= config.MIN_POPULATION) & (tracts["households"] >= config.MIN_HOUSEHOLDS)
    logger.info("  > %d tracts in the extract, %d residential (population >= %d, households >= %d)",
                len(tracts), int(residential.sum()), config.MIN_POPULATION, config.MIN_HOUSEHOLDS)
    return tracts[residential].reset_index(drop=True)


def complete(tracts: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Keep the tracts that have a value for every column an analysis needs."""
    kept = tracts.dropna(subset=columns).reset_index(drop=True)
    logger.info("  > %d of %d tracts have all %d inputs", len(kept), len(tracts), len(columns))
    return kept
