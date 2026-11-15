---
title: "GW-PCA"
tagline: "Standard and robust geographically weighted PCA: principal components that vary across space, with bandwidth and component selection and outlier-resistant estimation."
domain: spatial
stack: ["GWPCA", "Robust PCA", "Bandwidth selection", "Diagnostics"]
stats:
  - { value: "v5.2", label: "release" }
  - { value: "local", label: "components" }
  - { value: "robust", label: "outlier handling" }
order: 10
status: public
repo: "https://github.com/zihjyunderek/GW-PCA"
---

Global PCA assumes the relationships between variables are the same everywhere in your study area. For spatial data, that's usually false. **Geographically Weighted PCA (GWPCA)** lets the principal-component decomposition vary across space, revealing where the structure of multivariate relationships shifts.

> Confidential due to NDA.

## Method

The framework follows the methodology of Harris, Brunsdon and Charlton (2011) and runs on its peer-reviewed reference implementation, with the data handling, configuration and output built around it. It adds **robust GWPCA** with peer-reviewed outlier detection, important because a few anomalous locations can otherwise distort the local components everywhere nearby.

## Features

Dynamic model selection (choosing the number of components and bandwidth), comprehensive diagnostics, and production-grade output handling. It's built to be a reliable tool rather than a one-off script: versioned through v5.2, with the same scaffolding and configuration discipline as the rest of my spatial toolkit.
