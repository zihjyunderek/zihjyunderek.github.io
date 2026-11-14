---
title: "City-Typology"
tagline: "Which kinds of neighborhood design go with how residents rate their city: regional profiles from clustering, multipliers from MGWR, and competing dimension designs tested on a fixed gate across 15 cities."
domain: urban
stack: ["Python", "Factor analysis", "Genetic algorithm", "MGWR"]
stats:
  - { value: "15", label: "cities" }
  - { value: "6", label: "competing dimension splits" }
  - { value: "fixed", label: "gate before results" }
order: 7
status: private
---

The City Design Index reads a city as **regional profiles times multipliers**. Clusters of tracts that look alike on design metrics are the profiles; MGWR coefficients of the City Satisfaction Score on the design dimensions are the multipliers. Together they say which kinds of design go with how residents rate their city, and where. This project covers the insight paper that first read five cities this way and the typology work that tested its dimensions across 15.

> The survey, the metrics and every finding are confidential under NDA. This page describes the method.

## From metrics to multipliers

For every city the same chain runs, one stage after another:

1. **Metrics to factors.** About a hundred tract metrics are factor-analysed, with the number of factors set by a stated criterion.
2. **Factors to dimensions.** Factors are grouped into a few named design dimensions, mapped to a fixed vocabulary of dimension families so that cities compare like for like.
3. **Dimensions to indices.** A genetic algorithm picks, for each cluster and dimension, the metrics that compose the dimension's index.
4. **Indices to profiles.** K-Medoids on the dimension scores gives the regional profiles.
5. **Profiles to multipliers.** MGWR of the satisfaction score on the dimension indices, with one bandwidth per dimension, gives a multiplier for every tract, read by cluster.

## The insight paper

The insight paper read five cities, Washington, Austin, Miami, Dallas and Boston, cluster by cluster: within one profile, how strongly each design dimension moves satisfaction against the socio-economic baseline. Its evidence discipline carried into later work. Every number in the paper and its deck comes from one file regenerated from the model runs, nothing is typed by hand, and a city without a finished model carries its size and a "pending" status, never a placeholder result.

## Testing the dimensions themselves

A broad dimension may hide two things that pull apart. The typology work tested six competing ways to split one in two, three for urban form and three for mobility, against the same cluster partition as each city's baseline so that only the split changes. A split had to pass a gate written down before any result was seen. The test ran first on seven cities and was then repeated on all 15, so a split that only worked in a few cities could not carry the conclusion.
