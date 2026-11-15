---
title: "CDI-Demo"
tagline: "Self-contained dashboards that walk through the CDI method city by city: metrics, clusters, dimensions and the MGWR regression, with every cluster and dimension named by rule and audited."
domain: cdi
stack: ["Python", "Leaflet", "Plotly", "MGWR"]
stats:
  - { value: "6", label: "dashboard modes" }
  - { value: "2", label: "builders" }
  - { value: "9", label: "naming audit checks" }
order: 3
status: private
repo: "https://github.com/zihjyunderek/CDI_Demo"
---

The City Design Index runs a long chain for every city: about a hundred tract metrics, factor analysis, dimension indices, clusters, and an MGWR of resident satisfaction on the dimensions. CDI-Demo turns one run of that chain into a single HTML file that a reviewer can open without any setup and read from the first metric to the last coefficient.

> The dashboards hold survey results and are confidential under NDA. This page describes how they are built.

## Two builders, six modes

One builder writes a single multi-city demo with a switch between curated variants. The other writes one dashboard per experiment run, so runs can be compared side by side. They share their frontend, and every dashboard has the same six modes:

| Mode | What it shows |
| --- | --- |
| Overview | The city, the outcome and the run at a glance |
| Metrics | Every tract metric, mapped and described |
| Clusters | The tract clusters, their names and profiles |
| Dimensions | Which metrics build each dimension index, with their factor loadings |
| Regression | MGWR coefficients, bandwidths and significance by dimension |
| Census tracts | Any tract's full record |

## Names by rule

A cluster called "Urban Core" in one city has to mean the same thing in the next. Names are therefore derived, not written:

- **Clusters.** Each cluster gets a role vector of standardized metrics, compared by cosine similarity with a shared vocabulary of archetypes. A Hungarian assignment keeps two clusters of one city from taking the same name, and a cluster below a fixed similarity floor gets a new term instead of a forced one.
- **Dimensions.** A dimension takes one of five canonical names when its predictors are dominated by that theme, and keeps its own name otherwise, so the same construct carries the same name in every city.
- **Audit.** Nine consistency checks run across all cities, and every built dashboard is verified against the files it was built from.

## Reading the regression honestly

In these models the local intercept often explains most of the fit. The Regression mode therefore splits the model R² with a Shapley decomposition: the shares of the dimensions and the intercept add up to the model R² exactly, so a dimension's share is always what it adds beyond the baseline.
