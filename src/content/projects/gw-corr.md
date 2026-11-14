---
title: 'GW-Corr'
tagline: 'Geographically weighted Pearson correlation as a surface: four kernel families, a vectorized computation engine, significance masks, and a clean API.'
domain: spatial
stack: ['Python', 'NumPy (vectorized)', 'SciPy', 'Matplotlib']
stats:
  - { value: '4', label: 'kernel functions' }
  - { value: 'vectorized', label: 'computation engine' }
  - { value: 'API-first', label: 'package design' }
featured: false
order: 10
status: research
---

A single correlation coefficient for an entire city is a fiction: income and green space may correlate positively uptown and negatively downtown. **GW-Corr computes correlation as a surface**: a local Pearson coefficient at every location, weighted by spatial proximity.

> Confidential due to NDA.

## Features

- **Kernel library**: Gaussian, bi-square, exponential, and adaptive weight functions, selectable per analysis.
- **Vectorized engine**: distance matrices and weighted moments computed in NumPy batch operations rather than per-point loops, keeping city-scale runs fast.
- **Rich outputs**: local correlation surfaces, significance masks, and comparison plots between kernels.
- **Library ergonomics**: versioned package layout, documented API, and examples; built to be `pip install`-able rather than a one-off script.

## Role in the toolchain

GW-Corr is the reconnaissance step of my spatial workflow: before fitting MGWR or clustering archetypes, local correlation maps show *where* relationships flip sign, and which variables deserve spatially varying coefficients at all.
