---
title: "K-Medoids Archetype Pipeline"
tagline: "A single-file, reproducible pipeline that groups census tracts into urban archetypes with FasterPAM K-Medoids and a geography-aware fused distance, producing clean labels plus one interactive map."
domain: urban
stack: ["Python", "K-Medoids", "FasterPAM", "Folium"]
stats:
  - { value: "1", label: "file, reproducible" }
  - { value: "fused", label: "distance metric" }
  - { value: "real", label: "tract centers" }
order: 10
status: private
---

The focused, production-grade core of my clustering work, built to consolidate three earlier scripts into one method that's correct, reproducible, and academically defensible, so I never have to wonder *which* version of K-Medoids produced a result.

> Confidential due to NDA.

## In one breath

For each city it reads the merged metrics file, cleans and scales the features, builds a distance matrix that blends geography with socioeconomic similarity, runs K-Medoids (FasterPAM) over a range of K, assigns each cluster a stable and meaningful label, and writes everything back out, plus a clickable dashboard covering every city.

## The deliberate choices

- **The `kmedoids` package (Rust FasterPAM, Schubert and Rousseeuw 2021)** rather than the slow, conflict-prone `sklearn-extra`: fast, reproducible, battle-tested.
- **RobustScaler** so outlier neighborhoods (extreme rent or pollution) don't distort the clustering.

It's a small codebase that does one thing extremely well, which is exactly the point.
