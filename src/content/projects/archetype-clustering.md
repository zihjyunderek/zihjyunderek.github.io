---
title: "Urban Archetypes by Clustering"
tagline: "Clustering US census tracts into urban archetypes from 137 isochrone-based metrics, using seven algorithms across three methodological families, with one interactive dashboard for all cities."
domain: urban
stack: ["Python", "scikit-learn", "HDBSCAN", "K-Medoids"]
stats:
  - { value: "31", label: "cities" }
  - { value: "137", label: "metrics" }
  - { value: "7", label: "algorithms" }
featured: true
order: 3
status: private
---

> Confidential due to NDA.

## The approach

Each city's census tracts are described by **137 isochrone metrics** (what's reachable within a walk, transit, or drive time) spanning mobility, land use, economic conditions, environmental quality, and urban form. Rather than trust a single clustering method, the pipeline runs **seven algorithms across three families**, each with preprocessing matched to its assumptions:

| Family | Algorithms | Features | Preprocessing |
| --- | --- | --- | --- |
| Numerical | K-Means, GMM-EM, Ward | 30 curated | PowerTransformer (Yeo-Johnson) |
| Spatial | K-Medoids (FasterPAM) | ~132 | RobustScaler + fused Haversine distance |
| Density | DBSCAN, HDBSCAN, OPTICS | 12 orthogonal | PowerTransformer (Yeo-Johnson) |

For every method and every K, it computes cluster-validity indices (Silhouette, Davies-Bouldin, Calinski-Harabasz) and writes everything into a single self-contained HTML dashboard you can explore interactively.

## Deliberate choices

Every methodological decision was made on purpose, not by default:

- **K-Medoids over K-Means** for the spatial family: medoids are *real tracts*, not abstract averages, so every cluster center is an actual neighborhood you can point to and describe. That's exactly what an "archetype" should be.
- **A fused distance matrix** blends socioeconomic similarity with geographic proximity, so tracts that are both *alike* and *near* land together.
- **RobustScaler** centers on the median and scales by IQR, essential when income, rent, and pollution are full of outlier tracts that would otherwise dominate plain standardization.

## Lineage

This pipeline consolidated three earlier, divergent clustering scripts into one correct, reproducible, academically defensible method, so there's never any doubt about *which* version of the analysis produced a given result.
