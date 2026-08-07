---
title: "Urban Spatial Exclusion Index (USEI)"
tagline: "A composite index quantifying spatial exclusion across US cities, turning many access and opportunity metrics into one interpretable, mapped score per tract."
domain: urban
stack: ["Python", "Composite Index", "GeoPandas", "Plotly"]
stats:
  - { value: "index", label: "composite score" }
  - { value: "tract", label: "resolution" }
  - { value: "interactive", label: "HTML maps" }
order: 11
status: private
---

Spatial exclusion, being cut off from jobs, services, and opportunity by where you live, is felt locally but hard to measure. The USEI condenses many access and opportunity metrics into a single, interpretable score per census tract, so exclusion can be mapped, compared, and tracked.

> Confidential due to NDA.

## Building a defensible index

A composite index is only as trustworthy as the choices behind it. This one is explicit about each step: which metrics enter, how they're normalized so no single unit dominates, how they're weighted, and how the result is validated. The output is rendered as interactive HTML maps so the score can be interrogated tract-by-tract rather than taken on faith: you can always trace a high exclusion score back to the components that drove it.

## Part of a family

The USEI sits alongside parallel composite indices in the same body of work (a Green Index and a Prosperity Index) that share its scaffolding and methodology but target different dimensions of urban life. Building them as a consistent family means the scores are directly comparable and the code is reusable, rather than each index being a bespoke one-off.
