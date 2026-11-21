---
title: "City-Size-Demo"
tagline: "54 global cities sized by administrative area and subdivision count, every boundary fetched from open government data or OpenStreetMap and every area checked against the official figure."
domain: urban
stack: ["Python", "GeoPandas", "Shapely", "OpenStreetMap", "Jenks natural breaks"]
stats:
  - { value: "54", label: "global cities" }
  - { value: "4", label: "boundary sources, government data first" }
  - { value: "3", label: "size classes" }
order: 10
status: private
repo: "https://github.com/zihjyunderek/City-Size-Demo"
---

A brief listed global cities with no geometry attached. City-Size-Demo resolves each city to a real administrative boundary, computes its geodesic area and the number of its administrative subdivisions, the cross-country counterpart of US census tracts, and sorts the cities into small, medium and large. It writes a table, a report, a shapefile per city and an interactive page.

> The brief and its results are internal to Gensler Research Institute. This page describes how the pipeline works.

## A source ladder

Each city declares its sources in order: government open data first (the Australian Bureau of Statistics, the US Census Bureau, Statistics Canada, Japan's MLIT), then OpenStreetMap, then geoBoundaries, and GADM as a last resort. A source wins only if its geodesic area matches the official reference within a tolerance. Among several candidates the closest match wins, so a city cannot be mistaken for its central district.

## Validation on every run

Each city carries the area its national statistics office or city government publishes. Every fetched polygon is checked against it and flagged ok, warn or fail in every output; a city without a boundary shows as pending, never as a placeholder shape. Composite definitions are built as geometry: Tokyo is the union of its 23 special wards, Guadalajara and Monterrey the unions of their metropolitan municipalities.

## Size classes

Fisher-Jenks natural breaks on log area set the three classes. Terciles and the mean plus or minus one standard deviation cross-check them, and the report states how often the three methods agree.

## Engineering

- **Plain Python with a disk cache.** Every HTTP response is cached, so a rerun costs no network, and no language model sits in the data path.
- **One coordinate system.** EPSG:4326 throughout, with areas computed on the ellipsoid.
- **One command.** Five stages, fetch, validate, classify, build outputs and build the page, run in order and resume where they stopped.
