---
title: 'MGWR Analysis Toolkit'
tagline: 'An end-to-end Python toolkit for Multiscale Geographically Weighted Regression: automated bandwidth calibration, full spatial diagnostics, and interactive mapping, batch-run across US cities.'
domain: spatial
stack: ['Python', 'mgwr', 'GeoPandas', 'Plotly', 'scikit-learn']
stats:
  - { value: '2', label: 'model families (GWR / MGWR)' }
  - { value: '4-stage', label: 'stepwise calibration' }
  - { value: '31', label: 'cities batch-ready' }
featured: false
order: 5
status: private
---

Classical regression assumes one coefficient fits the whole map. Cities disagree: the effect of transit access on rent in Midtown is not its effect in Queens. **Multiscale GWR lets every coefficient vary over space, each at its own bandwidth**, and this toolkit turns that method into a production pipeline.

It anchors my flagship study at Gensler Research Institute: *Decoding the City: Unveiling NYC's Geographical Phenomena with MGWR*.

> Confidential due to NDA.

## What it does

- **Automated calibration**: optimal bandwidth search for GWR and MGWR with adaptive or fixed kernels, plus a forward/backward stepwise workflow (`baseline → forward first stage → fine-tune → backward`) for variable selection.
- **Full diagnostics**: local and global model statistics, Moran's I spatial autocorrelation tests, VIF and condition-number collinearity checks, and AICc / R² / ENP model comparison.
- **Visualization suite**: significance-masked static coefficient maps, interactive Plotly HTML maps, GWR-vs-MGWR comparison panels, standardized-residual views, and bandwidth charts.
- **Batch architecture**: config-driven runs reproduce an identical analysis across any number of cities.

## Engineering notes

The repo is organized as composable analyzers (`mgwr_analyzer`, `cluster_analyzer`, `global_fa_analyzer`) with a shared config layer and utility modules, the same pattern I reuse across my statistical toolkits, so each new method ships with diagnostics and maps for free.
