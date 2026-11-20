---
title: "City-Typology"
tagline: "Which kinds of neighborhood design go with how residents rate their city: regional profiles from clustering, multipliers from MGWR, and competing dimension designs tested on a fixed gate across 15 cities."
domain: urban
stack: ["Python", "Factor analysis", "Genetic algorithm", "MGWR"]
stats:
  - { value: "15", label: "cities" }
  - { value: "6", label: "competing dimension splits" }
  - { value: "fixed", label: "gate before results" }
order: 9
status: private
repo: "https://github.com/zihjyunderek/City-Typology"
---

The City Design Index reads a city as **regional profiles times multipliers**. Clusters of tracts that look alike on design metrics are the profiles; MGWR coefficients of the City Satisfaction Score on the design dimensions are the multipliers. Together they say which kinds of design go with how residents rate their city, and where. This project tests the dimensions themselves across 15 cities; the papers that report the method and the first five cities are in CDI-Papers.

> The survey, the metrics and every finding are confidential under NDA. This page describes the method.

## From metrics to multipliers

For every city the same chain runs, one stage after another:

1. **Metrics to factors.** About a hundred tract metrics are factor-analysed, with the number of factors set by a stated criterion.
2. **Factors to dimensions.** Factors are grouped into a few named design dimensions, mapped to a fixed vocabulary of dimension families so that cities compare like for like.
3. **Dimensions to indices.** A genetic algorithm picks, for each cluster and dimension, the metrics that compose the dimension's index.
4. **Indices to profiles.** K-Medoids on the dimension scores gives the regional profiles.
5. **Profiles to multipliers.** MGWR of the satisfaction score on the dimension indices, with one bandwidth per dimension, gives a multiplier for every tract, read by cluster.

## Testing the dimensions themselves

A broad dimension may hide two things that pull apart. The typology work tested six competing ways to split one in two, three for urban form and three for mobility, against the same cluster partition as each city's baseline so that only the split changes. A split had to pass a gate written down before any result was seen. The test ran first on seven cities and was then repeated on all 15, so a split that only worked in a few cities could not carry the conclusion.
