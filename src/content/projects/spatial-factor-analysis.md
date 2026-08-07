---
title: "Spatial Factor Analysis"
tagline: "A Python implementation of spatial factor-analysis methods from Thorson et al. (2015) and Berchuck et al. (2019), recovering latent spatial processes behind multivariate data."
domain: spatial
stack: ["Python", "NumPy", "Bayesian", "Factor Analysis"]
stats:
  - { value: "2", label: "papers implemented" }
  - { value: "latent", label: "spatial factors" }
  - { value: "Bayesian", label: "+ frequentist" }
order: 8
status: public
repo: "https://github.com/zihjyunderek/Spatial_FA"
---

Sometimes many observed variables are really driven by a few hidden spatial processes. **Spatial Factor Analysis (SFA)** recovers those latent processes, reducing dimensionality while explicitly modeling the spatial correlation that ordinary factor analysis ignores.

> Confidential due to NDA.

## Two methods, one toolkit

The implementation faithfully reproduces two key papers:

- **Thorson et al. (2015)**: spatial factor analysis for estimating joint distributions and correlations (originally for species ranges, but the math generalizes).
- **Berchuck et al. (2019)**: Bayesian non-parametric factor analysis for longitudinal spatial surfaces.

## Why it generalizes

SFA captures three things at once: spatial correlation within and between variables, the latent processes that drive observed patterns, and co-occurrence structure. That makes it useful far beyond its ecological origins: disease co-occurrence mapping in public health, regional socioeconomic structure in economics, and census-tract analysis in urban planning. Bringing peer-reviewed Bayesian spatial methods into a clean Python codebase is the connective tissue between academic statistics and applied urban research.
