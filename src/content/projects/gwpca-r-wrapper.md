---
title: "Advanced GWPCA R-Wrapper"
tagline: "A Python framework for standard and robust Geographically Weighted PCA, bridging Python's workflow ergonomics with R's academically validated GWmodel package."
domain: spatial
stack: ["Python", "R", "GWmodel", "rpy2"]
stats:
  - { value: "v5.2", label: "release" }
  - { value: "2", label: "languages bridged" }
  - { value: "robust", label: "outlier handling" }
order: 6
status: public
repo: "https://github.com/zihjyunderek/GWPCA"
---

Global PCA assumes the relationships between variables are the same everywhere in your study area. For spatial data, that's usually false. **Geographically Weighted PCA (GWPCA)** lets the principal-component decomposition vary across space, revealing where the structure of multivariate relationships shifts.

> Confidential due to NDA.

## The bridge

R's `GWmodel` package has the canonical, peer-reviewed GWPCA implementation, but R is awkward for the data wrangling, configuration, and visualization around the analysis. Python is the reverse. This framework gets the best of both: Python orchestrates data handling, config, and output, while R does the statistically validated heavy lifting underneath.

The implementation follows the seminal methodology of Harris, Brunsdon and Charlton (2011), and adds **robust GWPCA** with peer-reviewed outlier detection, important because a few anomalous locations can otherwise distort the local components everywhere nearby.

## Features

Dynamic model selection (choosing the number of components and bandwidth), comprehensive diagnostics, and production-grade output handling. It's built to be a reliable tool rather than a one-off script: versioned through v5.2, with the same scaffolding and configuration discipline as the rest of my spatial toolkit.
