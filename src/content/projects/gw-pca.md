---
title: "GW-PCA"
tagline: "Standard and robust geographically weighted PCA: principal components that vary across space, with bandwidth and component selection and outlier-resistant estimation."
domain: spatial
stack: ["GWPCA", "R GWmodel", "Robust PCA", "Bandwidth selection"]
stats:
  - { value: "3", label: "code generations, all kept" }
  - { value: "local", label: "components" }
  - { value: "robust", label: "outlier handling" }
order: 12
status: public
repo: "https://github.com/zihjyunderek/GW-PCA"
---

Global PCA assumes the relationships between variables are the same everywhere in your study area. For spatial data, that's usually false. **Geographically Weighted PCA (GWPCA)** lets the principal-component decomposition vary across space, revealing where the structure of multivariate relationships shifts.

> Confidential due to NDA.

## Method

The framework follows the methodology of Harris, Brunsdon and Charlton (2011) and runs on its peer-reviewed reference implementation, with the data handling, configuration and output built around it. It adds **robust GWPCA** with peer-reviewed outlier detection, important because a few anomalous locations can otherwise distort the local components everywhere nearby.

## Features

Dynamic model selection (choosing the number of components and bandwidth), comprehensive diagnostics, and production-grade output handling. The code went through three generations, all kept with their history: a first implementation in pure Python, an R-Wrapper around GWmodel (ver5.18 to ver5.26), and the current two packages, one for the model and one for clusters and maps.
