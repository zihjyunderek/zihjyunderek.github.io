---
title: "City Satisfaction Score Dashboard"
tagline: "Reverse-engineering an undocumented composite satisfaction score from delivered data alone, verified numerically to CSV-rounding precision at every pipeline run."
domain: urban
stack: ["Python", "Pandas", "Reverse Engineering", "Dashboard"]
stats:
  - { value: "≤1.3e-4", label: "max verified error" }
  - { value: "3", label: "cities" }
  - { value: "v4", label: "pipeline" }
order: 13
status: private
---

A colleague delivered a composite City Satisfaction Score across three cities, with no methodology documentation. Rather than treat it as a black box, I derived its structure mathematically from the data itself and built a pipeline that re-verifies that structure on every run.

> Confidential due to NDA.

## Reverse-engineering, then locking it down

The delivered files contained the scores but not the recipe. By working backward from the numbers, I recovered the relationship: per travel mode (car, walk, transit), a mode score is the mean of a four-question satisfaction battery over geo-bootstrapped tract means; those mode scores then combine through per-tract travel-mode weights into the composite.

The crucial engineering decision: **the derived relationships are re-verified numerically at every pipeline run**, across all three cities, to a maximum absolute error of 1.3 × 10⁻⁴ (CSV rounding precision). So if an upstream input ever changes in a way that breaks the assumed structure, the pipeline catches it immediately rather than silently producing wrong scores. That's the difference between reverse-engineering something once and being able to *depend* on it.
