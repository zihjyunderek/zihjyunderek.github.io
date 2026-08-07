---
title: 'PyGWPCC: Geographically Weighted Correlation'
tagline: 'A package-grade Python library for Geographically Weighted Pearson Correlation Coefficients: four kernel families, a vectorized computation engine, and a clean API.'
domain: spatial
stack: ['Python', 'NumPy (vectorized)', 'SciPy', 'Matplotlib']
stats:
  - { value: '4', label: 'kernel functions' }
  - { value: 'vectorized', label: 'computation engine' }
  - { value: 'API-first', label: 'package design' }
featured: false
order: 9
status: research
---

A single correlation coefficient for an entire city is a fiction: income and green space may correlate positively uptown and negatively downtown. **PyGWPCC computes correlation as a surface**: a local Pearson coefficient at every location, weighted by spatial proximity.

> Confidential due to NDA.

## Features

- **Kernel library**: Gaussian, bi-square, exponential, and adaptive weight functions, selectable per analysis.
- **Vectorized engine**: distance matrices and weighted moments computed in NumPy batch operations rather than per-point loops, keeping city-scale runs fast.
- **Rich outputs**: local correlation surfaces, significance masks, and comparison plots between kernels.
- **Library ergonomics**: versioned package layout, documented API, and examples; built to be `pip install`-able rather than a one-off script.

## Role in the toolchain

GWPCC is the reconnaissance step of my spatial workflow: before fitting MGWR or clustering archetypes, local correlation maps show *where* relationships flip sign, and which variables deserve spatially varying coefficients at all.
