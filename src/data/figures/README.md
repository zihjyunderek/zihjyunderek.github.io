# Figure data

One folder per project, named after the project file. One CSV per figure or table. `Figure.astro` reads these files when the site is built, and what a CSV says is what the figure prints.

Everything here is published with the site. Only numbers that may be public belong here: published results, public data, or simulated data. The project's frontmatter says which (`basis`).

## Transcribed from a publication

| File | Source | How it was made |
| --- | --- | --- |
| `implied-vol-var/breach_ratio_1pct.csv` | NCCU master's thesis (2026), Table 5-2 | Transcribed by hand: 13 models by 7 currency pairs, breach ratio in percent. |
| `implied-vol-var/basel_zone.csv` | Same thesis, Table 5-10 | Transcribed by hand: `zone` is the rating, `code` the letter printed in the table. |

## Built from public data

Source: U.S. Census Bureau, American Community Survey 2019–2023 5-year estimates, census tracts of the five New York City counties, downloaded once by `scripts/fetch_acs.py` into `scripts/figures/data/acs/`. Rebuild with `python scripts/build_figures.py`; settings in `scripts/figures/config.py`.

| Folder | Built by | Files |
| --- | --- | --- |
| `multiscale-gwr/` | `scripts/figures/s02_mgwr.py` | `forward_selection.csv`, `model_comparison.csv`, `bandwidths.csv`, `coefficients.csv`, `diagnostics.csv`, `residuals.csv` |
| `city-clusters/` | `scripts/figures/s03_archetypes.py` | `validity.csv`, `density_family.csv`, `archetype_map.csv`, `agreement.csv`, `geography_map.csv`, `medoids.csv`, `profiles.csv` |
| `city-indices/` | `scripts/figures/s04_exclusion_index.py` | `components.csv`, `index_map.csv`, `borough_profile.csv`, `robustness.csv` |

Maps draw each tract from `geometry/nyc_tracts.json`: one SVG path per GEOID, in drawing units, written by stage `geometry` (`scripts/figures/s06_geometry.py`) from `scripts/figures/data/geometry/nyc_tracts_2023.shp`. Those shapes are U.S. Census Bureau TIGER/Line 2023 census tracts clipped to the shoreline, saved once by `scripts/extract_tracts.py` with GEOID as their only attribute. The map CSVs name each tract by GEOID and carry no coordinates.

`cdi-milestone/study_cities.csv` and `geometry/study_cities.json` are an illustration, not an analysis: the census tracts of the 15 CDI study cities, each city fitted to its own square, shaded by tract area within the city. `scripts/draw_study_cities.py` draws them from TIGER/Line 2023 tract layers, reading nothing but the shapes and the land area (to leave water-only tracts out). The layers are about 30 MB and are not committed.

These pages describe client work whose data is confidential. Their figures show the same methods on public data and are not the client's results.

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.

## Simulated

| Folder | Built by | Files |
| --- | --- | --- |
| `city-survey/` | `scripts/figures/s05_satisfaction.py` | `structure_errors.csv`, `verification.csv` |

No public survey has the structure of the delivered files, so this page uses simulated ones (fixed seed).
