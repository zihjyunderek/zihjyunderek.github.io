---
title: "Gensler-data"
tagline: "One store for the data behind the City Design Index: tract metrics, ACS extracts and census boundaries for 32 US cities, rebuilt into PostgreSQL with PostGIS and checked file by file."
domain: cdi
stack: ["PostgreSQL", "PostGIS", "Python", "Docker", "Census API"]
stats:
  - { value: "32", label: "US cities" }
  - { value: "14,748", label: "census tracts in the ACS layer" }
  - { value: "51", label: "ACS columns per tract" }
order: 4
status: private
repo: "https://github.com/zihjyunderek/Gensler-data"
---

Every CDI repository used to carry its own copy of the tract data, and the copies had started to drift apart. Gensler-data keeps one verified copy of each layer for 32 US cities, and a PostgreSQL database with PostGIS rebuilt from those files, so a model reads one source and joining two layers is a query.

> The survey responses and the design metrics belong to Gensler Research Institute and are confidential under NDA. This page describes the store and shows only its public census layer.

## Four layers

| Layer | Per city | Source |
| --- | --- | --- |
| Boundaries | census tracts, ZIP code areas and the city limit | TIGER/Line, U.S. Census Bureau |
| ACS | 51 columns per census tract | American Community Survey 5-year estimates, 2024 |
| Metrics | design and socio-economic metrics per tract | built in City-Survey, confidential |
| Survey | city satisfaction survey, 2025 and 2026 waves | Gensler Research Institute, confidential |

## The ACS layer

The ACS extract comes from the Census API, one file per city, keyed by the 11-digit tract GEOID.

| Census table | What it gives per tract | Columns |
| --- | --- | --- |
| B01001, sex by age | population, and age brackets in total and by sex | 24 |
| B19013, B19301 | median household income and per-capita income | 2 |
| B15003 | educational attainment of the population 25 and over | 10 |
| B08301, means of transportation to work | workers by mode, each mode's share, and weights over car, transit and walking | 10 |
| Geography | tract identifiers | 5 |

Census "jam values" (−666,666,666 and below) become missing values before any aggregation.

## The database

- **Rebuilt, never edited.** A loader drops and rebuilds every table from the files. The files stay the source of truth, so the database can be thrown away at any time.
- **Checked file by file.** A round-trip test reads every loaded file back out of the database and compares it value by value, geometries included. All 31 ACS files, 32 metrics files, 59 survey files and every boundary file pass.
- **Built to join.** Every row keeps its city, file and position. Census codes are stored as text, so the ACS, the metrics and the boundaries join on the tract GEOID.
- **Local only.** The database runs in Docker on 127.0.0.1, with its password in a file git ignores, because two of its layers are confidential.
- **Backed up first.** The local folder was copied and checked against a SHA-256 list before the database was introduced.
