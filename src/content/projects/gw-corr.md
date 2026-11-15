---
title: 'GW-Corr'
tagline: 'Geographically weighted correlation and summary statistics as surfaces: local means, spreads, quantiles and correlations at every location, validated statistic by statistic against GWmodel.'
domain: spatial
stack: ['Python', 'NumPy (vectorized)', 'SciPy', 'Matplotlib']
stats:
  - { value: '5', label: 'kernels, fixed or adaptive' }
  - { value: '11', label: 'local statistics per variable or pair' }
  - { value: '1e-9', label: 'largest relative gap to GWmodel' }
featured: false
order: 11
status: research
repo: 'https://github.com/zihjyunderek/GW-Corr'
---

A single correlation coefficient for an entire city is a fiction: income and green space may correlate positively uptown and negatively downtown. **GW-Corr computes correlation as a surface**: a local Pearson coefficient at every location, weighted by spatial proximity.

> The data it was built for are confidential under NDA. The package and its tests run on simulated data.

## Features

- **The full GW summary statistics** (Brunsdon, Fotheringham and Charlton, 2002): local mean, standard deviation, variance, skewness and coefficient of variation for every variable; covariance, Pearson and Spearman correlation for every pair; and the weighted median, interquartile range and quantile imbalance.
- **Kernels and distances**: bi-square, tri-cube, Gaussian, exponential and box-car kernels, each with a fixed or adaptive bandwidth, on Minkowski, rotated or ellipsoidal great-circle distances.
- **Inference**: a local t-test with an effective sample size and a Fisher-z interval for every correlation, and a randomisation test for every statistic.
- **Bandwidth selection** by leave-one-out cross-validation with a golden-section search.
- **Vectorized engine**: weighted moments in NumPy batch operations over blocks of locations, so city-scale runs stay fast and memory stays bounded.

## Validation

Every statistic, for all five kernels, fixed and adaptive, matches GWmodel's `gwss()` (Gollini et al., 2015) to a relative 1e-9, and so do the distance options and the bandwidth search. The checks found two places where GWmodel departs from the method it implements: its Monte Carlo test reorders the observed statistics instead of recomputing them on permuted data, and its cross-validation score drives the bandwidth to the top of its range. GW-Corr follows the method in both.

## Role in the toolchain

GW-Corr is the reconnaissance step of my spatial workflow: before fitting MGWR or clustering archetypes, local correlation maps show *where* relationships flip sign, and which variables deserve spatially varying coefficients at all.
