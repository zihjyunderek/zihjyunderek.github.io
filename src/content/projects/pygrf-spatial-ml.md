---
title: "Spatially-Explicit Feature Selection with PyGRF"
tagline: "A Geographical Random Forest approach to multi-city variable prediction: theory-informed hyperparameters, local training-sample expansion, and spatially-weighted local prediction."
domain: spatial
stack: ["Python", "PyGRF", "Random Forest", "scikit-learn"]
stats:
  - { value: "Local", label: "model fitting" }
  - { value: "Multi-city", label: "prediction" }
  - { value: "Moran's I", label: "residual check" }
order: 7
status: public
repo: "https://github.com/zihjyunderek/PyGRF"
---

Random forests are powerful but spatially naive: they treat a tract in Boston and a tract in Phoenix as exchangeable rows. **Geographical Random Forest (GRF)** fixes that by fitting a local forest around each location, so the model can learn that the drivers of an outcome differ across geography.

> Confidential due to NDA.

## What's inside

This project is a full research implementation, not just a model call:

- **Theory-informed hyperparameter determination**: local model size and bandwidth chosen from spatial reasoning rather than blind grid search.
- **Local training-sample expansion**: each local forest borrows nearby observations to avoid starving on sparse neighborhoods.
- **Spatially-weighted local prediction**: predictions weight nearby training points more heavily, respecting Tobler's first law.

## Evaluation

The analysis goes beyond a single accuracy number: it compares model performance against global baselines, examines per-location **feature importance** (which drivers matter *where*), and runs **spatial autocorrelation analysis on the residuals**, because a good spatial model should leave residuals with no remaining spatial pattern. The README walks through results interpretation and the geographical insights that fall out of the local feature-importance surfaces.
