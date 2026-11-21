---
title: "GW-RF"
tagline: "Geographically weighted random forest for multi-city prediction: theory-informed hyperparameters, local training-sample expansion, and spatially weighted local prediction."
domain: spatial
stack: ["Geographical Random Forest", "Local feature importance", "SHAP", "Moran's I"]
stats:
  - { value: "Local", label: "model fitting" }
  - { value: "Multi-city", label: "prediction" }
  - { value: "Moran's I", label: "residual check" }
order: 11
status: public
repo: "https://github.com/zihjyunderek/PyGRF"
---

Random forests are powerful but spatially naive: they treat a tract in Boston and a tract in Phoenix as exchangeable rows. A **geographically weighted random forest** (Geographical Random Forest, GRF) fixes that by fitting a local forest around each location, so the model can learn that the drivers of an outcome differ across geography.

> Confidential due to NDA.

## What's inside

This project is a full research implementation, not just a model call:

- **Theory-informed hyperparameter determination**: local model size and bandwidth chosen from spatial reasoning rather than blind grid search.
- **Local training-sample expansion**: each local forest borrows nearby observations to avoid starving on sparse neighborhoods.
- **Spatially-weighted local prediction**: predictions weight nearby training points more heavily, respecting Tobler's first law.

## Evaluation

The analysis goes beyond a single accuracy number: it compares model performance against global baselines, examines per-location **feature importance** (which drivers matter *where*), and runs **spatial autocorrelation analysis on the residuals**, because a good spatial model should leave residuals with no remaining spatial pattern. The local feature-importance surfaces then show which drivers matter where.
