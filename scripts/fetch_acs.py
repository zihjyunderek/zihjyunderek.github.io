"""Download, once, the public ACS extract the project figures are built from.

    python scripts/fetch_acs.py --key YOUR_KEY     # first run
    python scripts/fetch_acs.py --key YOUR_KEY --force   # download again

Source: U.S. Census Bureau, American Community Survey 5-year estimates
(2019-2023), every census tract in the five New York City counties, from the
official Data API; tract centroids and land area from the Census Gazetteer.

The result is public data and is committed, so building the figures never
needs the network or a key. The key itself is a secret: pass it with --key,
or set CENSUS_API_KEY, or put `CENSUS_API_KEY=...` in the gitignored `.env`.
A key is free: https://api.census.gov/data/key_signup.html

Writes, under scripts/figures/data/acs/:
  * nyc_tracts_acs5_2023.csv          one row per tract, raw counts and medians
  * nyc_tracts_acs5_2023.columns.csv  each column's ACS code and official label

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

logger = logging.getLogger("fetch_acs")

# ==========================================================================
# [Config] What to download
# ==========================================================================
YEAR = 2023
STATE = "36"  # New York
COUNTIES = {"005": "Bronx", "047": "Brooklyn", "061": "Manhattan", "081": "Queens", "085": "Staten Island"}

API = f"https://api.census.gov/data/{YEAR}/acs/acs5"
GAZETTEER = f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/{YEAR}_Gazetteer"
GAZETTEER_STATE = f"{GAZETTEER}/{YEAR}_gaz_tracts_{STATE}.txt"
GAZETTEER_NATIONAL = f"{GAZETTEER}/{YEAR}_Gaz_tracts_national.zip"
KEY_SIGNUP = "https://api.census.gov/data/key_signup.html"

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "scripts" / "figures" / "data" / "acs"
OUT_CSV = OUT_DIR / f"nyc_tracts_acs5_{YEAR}.csv"
OUT_COLUMNS = OUT_DIR / f"nyc_tracts_acs5_{YEAR}.columns.csv"

# column name -> (ACS code, text the official label must contain). The label
# check runs before any data is downloaded, so a wrong code can never be
# saved under the wrong name.
VARIABLES: dict[str, tuple[str, str]] = {
    "total_population": ("B01003_001E", "total"),
    "median_age": ("B01002_001E", "median age"),
    "median_household_income": ("B19013_001E", "median household income"),
    "gini_index": ("B19083_001E", "gini index"),
    "median_gross_rent": ("B25064_001E", "median gross rent"),
    "median_rent_pct_of_income": ("B25071_001E", "median gross rent as a percentage of household income"),
    "median_home_value": ("B25077_001E", "median value"),
    "median_year_built": ("B25035_001E", "median year structure built"),
    "median_rooms": ("B25018_001E", "median number of rooms"),
    "housing_units": ("B25002_001E", "total"),
    "vacant_units": ("B25002_003E", "vacant"),
    "occupied_units": ("B25003_001E", "total"),
    "renter_occupied_units": ("B25003_003E", "renter occupied"),
    "units_by_year_built": ("B25034_001E", "total"),
    "units_built_2020_or_later": ("B25034_002E", "built 2020 or later"),
    "units_built_2010_to_2019": ("B25034_003E", "built 2010 to 2019"),
    "units_built_1939_or_earlier": ("B25034_011E", "built 1939 or earlier"),
    "population_25_plus": ("B15003_001E", "total"),
    "bachelors_degree": ("B15003_022E", "bachelor's degree"),
    "masters_degree": ("B15003_023E", "master's degree"),
    "professional_degree": ("B15003_024E", "professional school degree"),
    "doctorate_degree": ("B15003_025E", "doctorate degree"),
    "poverty_universe": ("B17001_001E", "total"),
    "below_poverty": ("B17001_002E", "below poverty level"),
    "civilian_labor_force": ("B23025_003E", "civilian labor force"),
    "unemployed": ("B23025_005E", "unemployed"),
    "workers": ("B08301_001E", "total"),
    "commute_public_transit": ("B08301_010E", "public transportation"),
    "commute_bicycle": ("B08301_018E", "bicycle"),
    "commute_walked": ("B08301_019E", "walked"),
    "worked_from_home": ("B08301_021E", "worked from home"),
    "households": ("B08201_001E", "total"),
    "households_no_vehicle": ("B08201_002E", "no vehicle available"),
    "households_internet_universe": ("B28002_001E", "total"),
    "households_no_internet": ("B28002_013E", "no internet access"),
    "nativity_universe": ("B05002_001E", "total"),
    "foreign_born": ("B05002_013E", "foreign born"),
    "occupants_per_room_universe": ("B25014_001E", "total"),
    "owner_crowded_1_01_to_1_50": ("B25014_005E", "1.01 to 1.50"),
    "owner_crowded_1_51_to_2_00": ("B25014_006E", "1.51 to 2.00"),
    "owner_crowded_2_01_or_more": ("B25014_007E", "2.01 or more"),
    "renter_crowded_1_01_to_1_50": ("B25014_011E", "1.01 to 1.50"),
    "renter_crowded_1_51_to_2_00": ("B25014_012E", "1.51 to 2.00"),
    "renter_crowded_2_01_or_more": ("B25014_013E", "2.01 or more"),
}

# The API marks "no estimate" with large negative sentinels such as -666666666.
MISSING_BELOW = -100_000_000
TIMEOUT_SECONDS = 60
SQM_PER_SQKM = 1_000_000


class FetchError(RuntimeError):
    """A download failed in a way the user can act on."""


def read_key(cli_key: str | None) -> str | None:
    """Return the API key from --key, the environment, or the gitignored .env."""
    if cli_key:
        return cli_key.strip()
    if os.environ.get("CENSUS_API_KEY"):
        return os.environ["CENSUS_API_KEY"].strip()
    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "CENSUS_API_KEY" and value.strip():
                return value.strip().strip("\"'")
    return None


def get(url: str) -> bytes:
    """Fetch one URL, turning network failures into a readable error."""
    request = urllib.request.Request(url, headers={"User-Agent": "zihjyunderek.github.io figure build"})
    shown = re.sub(r"[?&]key=[^&]*", "", url)  # never echo the key
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:300]
        raise FetchError(f"HTTP {error.code} from {shown}\n  {body}") from error
    except urllib.error.URLError as error:
        raise FetchError(f"Could not reach {shown}\n  {error.reason}") from error


def get_api(path_and_query: str, key: str | None) -> object:
    """Call the Census Data API and return parsed JSON."""
    url = f"{API}{path_and_query}"
    if key:
        url += ("&" if "?" in url else "?") + "key=" + urllib.parse.quote(key)
    body = get(url).decode("utf-8", errors="replace")
    try:
        return json.loads(body)
    except json.JSONDecodeError as error:
        if "key" in body.lower():
            raise FetchError(
                "The Census API refused the request because of the API key.\n"
                f"  Get a free key at {KEY_SIGNUP}, activate it from the email,\n"
                "  then run: python scripts/fetch_acs.py --key YOUR_KEY"
            ) from error
        raise FetchError(f"Unexpected reply from the Census API:\n  {body[:300]}") from error


def plain(text: str) -> str:
    """Lower-case a label and turn its punctuation into spaces.

    Official labels vary in punctuation ("Foreign-born:", "Bachelor's degree"),
    so labels are compared by their words. A decimal point is kept, because
    "1.01 to 1.50" must not match "101 to 150".
    """
    return re.sub(r"[^a-z0-9.]+", " ", text.lower()).strip()


def check_labels(key: str | None) -> dict[str, str]:
    """Confirm every code means what its column name says; return the labels."""
    labels: dict[str, str] = {}
    wrong: list[str] = []
    for column, (code, expected) in VARIABLES.items():
        meta = get_api(f"/variables/{code}.json", key)
        label = f"{meta.get('concept', '')}: {meta.get('label', '')}" if isinstance(meta, dict) else ""
        labels[column] = label
        if plain(expected) not in plain(label):
            wrong.append(f"{column}: {code} is '{label}', expected text '{expected}'")
    if wrong:
        raise FetchError("ACS codes do not match their column names:\n  " + "\n  ".join(wrong))
    return labels


def clean(value: object) -> str:
    """Return an API cell as text, blank when the API reports no estimate."""
    if value is None:
        return ""
    text = str(value)
    try:
        return "" if float(text) < MISSING_BELOW else text
    except ValueError:
        return text


def fetch_tracts(key: str | None) -> list[dict[str, str]]:
    """Download every variable for every tract, one county per request."""
    codes = [code for code, _ in VARIABLES.values()]
    rows: list[dict[str, str]] = []
    for fips, borough in COUNTIES.items():
        query = f"?get=NAME,{','.join(codes)}&for=tract:*&in=state:{STATE}&in=county:{fips}"
        table = get_api(query, key)
        if not isinstance(table, list) or len(table) < 2:
            raise FetchError(f"No tract rows returned for county {fips}.")
        header, *records = table
        for record in records:
            cell = dict(zip(header, record))
            row = {
                "geoid": f"{cell['state']}{cell['county']}{cell['tract']}",
                "borough": borough,
                "tract_name": str(cell["NAME"]),
            }
            for column, (code, _) in VARIABLES.items():
                row[column] = clean(cell[code])
            rows.append(row)
        logger.info("  > %s: %d tracts", borough, len(records))
    return rows


def parse_gazetteer(text: str) -> dict[str, dict[str, str]]:
    """Map tract GEOID to its centroid and land area, from Gazetteer text."""
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    reader.fieldnames = [name.strip() for name in (reader.fieldnames or [])]
    wanted = {f"{STATE}{fips}" for fips in COUNTIES}
    places: dict[str, dict[str, str]] = {}
    for line in reader:
        geoid = line["GEOID"].strip()
        if geoid[:5] in wanted:
            places[geoid] = {
                "lat": line["INTPTLAT"].strip(),
                "lon": line["INTPTLONG"].strip(),
                "land_sqkm": f"{int(line['ALAND']) / SQM_PER_SQKM:.4f}",
            }
    return places


def fetch_gazetteer() -> dict[str, dict[str, str]]:
    """Download tract centroids: the state file, else the national archive."""
    try:
        text = get(GAZETTEER_STATE).decode("utf-8", errors="replace")
    except FetchError as state_error:
        logger.info("  > state Gazetteer file not available, trying the national archive")
        try:
            archive = zipfile.ZipFile(io.BytesIO(get(GAZETTEER_NATIONAL)))
        except FetchError as national_error:
            raise FetchError(f"{state_error}\n{national_error}") from national_error
        text = archive.read(archive.namelist()[0]).decode("utf-8", errors="replace")
    places = parse_gazetteer(text)
    if not places:
        raise FetchError("The Gazetteer file has no tracts for the five counties.")
    return places


def write_outputs(rows: list[dict[str, str]], places: dict[str, dict[str, str]], labels: dict[str, str]) -> None:
    """Join centroids onto the tract rows and write both CSV files."""
    missing = [row["geoid"] for row in rows if row["geoid"] not in places]
    if missing:
        raise FetchError(f"{len(missing)} tracts have no Gazetteer centroid, e.g. {missing[:3]}.")
    lead = ["geoid", "borough", "tract_name", "lat", "lon", "land_sqkm"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*lead, *VARIABLES], lineterminator="\n")
        writer.writeheader()
        for row in sorted(rows, key=lambda r: r["geoid"]):
            writer.writerow({**row, **places[row["geoid"]]})
    with OUT_COLUMNS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["column", "acs_code", "official_label"])
        writer.writerow(["lat, lon, land_sqkm", "", f"{YEAR} Census Gazetteer: internal point and land area"])
        for column, (code, _) in VARIABLES.items():
            writer.writerow([column, code, labels[column]])


def main(argv: list[str] | None = None) -> int:
    """Download the extract unless it is already there; return an exit code."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="Download the ACS extract behind the project figures.")
    parser.add_argument("--key", help="Census API key (or set CENSUS_API_KEY, or put it in .env)")
    parser.add_argument("--force", action="store_true", help="download again even if the file exists")
    args = parser.parse_args(argv)

    if OUT_CSV.is_file() and not args.force:
        logger.info("Already downloaded: %s (use --force to refresh)", OUT_CSV.relative_to(REPO_ROOT).as_posix())
        return 0

    key = read_key(args.key)
    try:
        logger.info("--- ACS %d 5-year, New York City tracts ---", YEAR)
        logger.info("  > checking %d variable codes against the official labels", len(VARIABLES))
        labels = check_labels(key)
        rows = fetch_tracts(key)
        logger.info("  > tract centroids from the Gazetteer")
        places = fetch_gazetteer()
        write_outputs(rows, places, labels)
    except FetchError as error:
        logger.error("\n[ERROR] %s", error)
        return 1
    logger.info("  > wrote %d tracts to %s", len(rows), OUT_CSV.relative_to(REPO_ROOT).as_posix())
    logger.info("Done. Tell Claude the file is there, or commit it yourself.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
