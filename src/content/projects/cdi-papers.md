---
title: "CDI-Papers"
tagline: "The two papers of the City Design Index: a methodology paper on how the index is built from public sources, and an insight paper that reads five cities cluster by cluster, every number traced to one file."
domain: cdi
stack: ["Python", "Node.js", "Word and PowerPoint builders", "Disclosure checks"]
stats:
  - { value: "2", label: "papers" }
  - { value: "2", label: "methodology versions, review and submission" }
  - { value: "7", label: "insight paper releases" }
order: 2
status: private
repo: "https://github.com/zihjyunderek/CDI-Papers"
---

The City Design Index (CDI) at Gensler Research Institute reads a city as regional profiles times multipliers: clusters of tracts that look alike on design metrics, and MGWR coefficients of the City Satisfaction Score on the design dimensions. Two papers report it. The methodology paper explains how the engine works; the insight paper reports what it found. I built both, with their decks, from the model output.

> The survey, the model results and every finding are confidential under NDA. This page describes how the papers are made.

## The methodology paper

How the index is built from public sources (ACS, LEHD LODES, OpenStreetMap, FEMA, EPA, USGS), from tract metrics to factors, dimensions, indices, profiles and multipliers. It comes in two versions from one source: a two-page review version that names the method families only, and an eight-page submission version with full disclosure. A disclosure check keeps anything beyond the method families out of the review version, and a numbers check ties every figure in both to the canonical file.

## The insight paper

The insight paper reads five cities, Washington, Austin, Miami, Dallas and Boston, cluster by cluster: within one regional profile, how strongly each design dimension moves satisfaction against the socio-economic baseline. City-specific dimension names are mapped to four fixed dimension families, so the cities compare like for like. It went through seven releases, each kept with the requests and reviewer answers that led to the next.

## One file of numbers

Neither paper runs a model; the model output is an input. Every number in the papers and their decks comes from one file of canonical numbers, regenerated from the model runs by a script, and nothing is typed by hand. A city without a finished model carries its size and a "pending" status, never a placeholder result. One rounding rule applies in every builder, so a value never prints two ways.
