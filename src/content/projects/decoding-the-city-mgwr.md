---
title: "Decoding the City: NYC through MGWR"
tagline: "A multiscale geographically weighted regression toolkit that quantifies how urban indicators drive population, home prices, and rents, at the scale each process actually operates."
domain: spatial
stack: ["Python", "MGWR", "GWR", "GeoPandas", "Plotly"]
stats:
  - { value: "Multi", label: "scale bandwidths" }
  - { value: "Moran's I", label: "spatial diagnostics" }
  - { value: "AICc", label: "model selection" }
featured: true
order: 1
status: private
---

The legacy of my work at Gensler Research Institute(GRI). Conventional regression assumes one relationship holds everywhere: that an extra subway stop changes rents by the same amount in CBD as in the outer boroughs. Cities don't work that way. This toolkit replaces that assumption with **Multiscale Geographically Weighted Regression (MGWR)**, letting each predictor operate at its own spatial scale.

> Confidential due to NDA.

## What it does

The toolkit is an end-to-end solution from raw spatial data to publication-grade diagnostics:

- **Automatic model calibration**: selects optimal bandwidths for both GWR and MGWR using adaptive or fixed kernels, so each covariate gets the neighborhood size its process demands.
- **Full statistical battery**: local and global diagnostics, spatial autocorrelation testing (Moran's I), multicollinearity checks (VIF, condition number), and model-comparison metrics (AICc, R², ENP).
- **Advanced visualization suite**: significance-masked static maps, interactive Plotly HTML maps, GWR-vs-MGWR coefficient comparisons, standardized residual analysis, and bandwidth visualization.
- **Batch processing**: applies a consistent methodology across many cities, so results are comparable rather than bespoke.

## Why MGWR

A single global coefficient hides exactly the thing an urban researcher cares about: *where* a relationship is strong and *where* it inverts. Standard GWR improves on this but forces every variable to share one bandwidth. MGWR frees each predictor to act at its own scale, capturing that, say, demographic effects vary block-by-block while macro-accessibility effects vary across the whole metro. The result is a coefficient *surface* per variable, not a single number.

## Engineering notes

The pipeline is staged (`baseline → forward first stage → forward fine-tune → backward stepwise`), each an entry point that reads a shared config and writes versioned, reproducible output. Map generation is decoupled from model fitting so a re-render never forces a re-fit. This is the same scaffolding discipline I apply across every repo: numbered stages, one source of truth for configuration, and outputs that never overwrite their inputs.
