"""Settings shared by the figure builders: paths, the seed, and each analysis' inputs.

Every number a builder could be tempted to hard-code lives here, so a change of
specification is one edit and shows up in one diff.
"""

from __future__ import annotations

from pathlib import Path

# ==========================================================================
# [Config] Paths
# ==========================================================================
REPO_ROOT = Path(__file__).resolve().parents[2]
ACS_CSV = REPO_ROOT / "scripts" / "figures" / "data" / "acs" / "nyc_tracts_acs5_2023.csv"
TRACT_SHAPES = REPO_ROOT / "scripts" / "figures" / "data" / "geometry" / "nyc_tracts_2023.shp"
FIGURE_DATA = REPO_ROOT / "src" / "data" / "figures"
MAP_SHAPES = FIGURE_DATA / "geometry" / "nyc_tracts.json"

# ==========================================================================
# [Config] Map drawing (stage `geometry`)
# ==========================================================================
# Drawing units: a map is at most 30rem (480px) wide on screen, so one unit is
# half a pixel. Shapes are simplified by one unit and drawn in whole units.
MAP_WIDTH = 960
MAP_PAD = 10
MAP_TOLERANCE = 1.0
MAP_SHAPES_SOURCE = "U.S. Census Bureau, TIGER/Line 2023 census tracts, clipped to the shoreline"

# One seed for every stochastic step (k-means starts, bootstraps, simulation).
SEED = 20261114

# ==========================================================================
# [Config] Which tracts enter an analysis
# ==========================================================================
# Tracts below these sizes are parks, airports, jails and the like: their
# medians are missing or rest on a handful of households.
MIN_POPULATION = 500
MIN_HOUSEHOLDS = 200

# ==========================================================================
# [Config] Satisfaction score (simulated; no public survey has this structure)
# ==========================================================================
SATISFACTION_CITIES = {"City A": 180, "City B": 240, "City C": 150}  # tracts per city
SATISFACTION_MODES = ("Car", "Walk", "Transit")
SATISFACTION_QUESTIONS = 4
SATISFACTION_DECIMALS = 4  # the delivered CSVs are rounded to four decimals

# ==========================================================================
# [Config] MGWR: what explains rent, and at which spatial scale
# ==========================================================================
# column -> (label on the figures, take the logarithm first)
MGWR_TARGET = ("median_gross_rent", "Median gross rent", True)
MGWR_CANDIDATES: dict[str, tuple[str, bool]] = {
    "median_household_income": ("Household income", True),
    "median_rooms": ("Rooms per home", False),
    "transit_share": ("Transit commuters", False),
    "prewar_share": ("Pre-1940 homes", False),
    "college_share": ("College degree", False),
    "density": ("Population density", True),
    "foreign_born_share": ("Foreign born", False),
    "median_age": ("Median age", False),
}
# Forward selection stops when the best remaining candidate lowers AICc by less than this.
STEPWISE_MIN_GAIN = 10.0
STEPWISE_MAX_TERMS = 5
INTERCEPT_LABEL = "Baseline (intercept)"
MORAN_NEIGHBOURS = 8
MORAN_PERMUTATIONS = 999

# ==========================================================================
# [Config] Archetypes: clustering tracts
# ==========================================================================
# column -> (label on the figures, take the logarithm first)
ARCHETYPE_FEATURES: dict[str, tuple[str, bool]] = {
    "density": ("Population density", True),
    "median_household_income": ("Household income", True),
    "median_gross_rent": ("Gross rent", True),
    "median_age": ("Median age", False),
    "college_share": ("College degree", False),
    "poverty_rate": ("Poverty rate", False),
    "renter_share": ("Renters", False),
    "prewar_share": ("Pre-1940 homes", False),
    "transit_share": ("Transit commuters", False),
    "no_vehicle_share": ("No vehicle", False),
    "foreign_born_share": ("Foreign born", False),
    "crowded_share": ("Crowded homes", False),
}
ARCHETYPE_K_RANGE = range(2, 9)
ARCHETYPE_K = 5  # the number of archetypes mapped; five is also what the map can color apart
GEOGRAPHY_WEIGHT = 0.2  # share of the fused distance that is plain distance on the ground
GEOGRAPHY_WEIGHTS = {"Features only": 0.0, "20% geography": 0.2, "40% geography": 0.4}
DENSITY_COMPONENTS = 4  # principal components fed to the density-based methods
DENSITY_MIN_SAMPLES = 10
HDBSCAN_MIN_CLUSTER = 30
# columns shown for each medoid tract: column -> (table header, decimals)
MEDOID_COLUMNS: dict[str, tuple[str, int]] = {
    "density": ("People per km²", 0),
    "median_household_income": ("Income, $", 0),
    "median_gross_rent": ("Rent, $", 0),
    "transit_share": ("Transit, %", 0),
}

# ==========================================================================
# [Config] Exclusion index: an illustration on ACS proxies
# ==========================================================================
# column -> (component, dimension, ACS table); every component rises with exclusion
EXCLUSION_COMPONENTS: dict[str, tuple[str, str, str]] = {
    "poverty_rate": ("Poverty", "Economy", "B17001"),
    "unemployment_rate": ("Unemployment", "Economy", "B23025"),
    "median_rent_pct_of_income": ("Rent burden", "Housing", "B25071"),
    "crowded_share": ("Crowding", "Housing", "B25014"),
    "no_internet_share": ("No internet", "Access", "B28002"),
    "no_college_share": ("No college degree", "Access", "B15003"),
}
EXCLUSION_WINSOR = (0.01, 0.99)  # percentiles the components are clipped to before scaling
INDEX_LABEL = "Exclusion index"
