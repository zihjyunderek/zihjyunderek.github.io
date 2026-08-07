---
title: "Python Notebook Toolkit"
tagline: "A collection of small, sharp Jupyter utilities for the unglamorous first hour of every analysis: inspecting structure, columns, missing values, and merging messy CSVs."
domain: engineering
stack: ["Python", "Jupyter", "Pandas"]
stats:
  - { value: "6", label: "utilities" }
  - { value: "0", label: "setup friction" }
  - { value: "daily", label: "use" }
order: 14
status: public
repo: "https://github.com/zihjyunderek/Python-Notebook-Toolkit"
---

Every analysis starts the same way: figure out what's in the folder, what's in the files, and what's broken about them. This toolkit packages that first hour into a handful of reusable Jupyter notebooks so it never has to be re-improvised.

## The utilities

- **Directory structure**: print a folder tree so you can see the data layout at a glance.
- **Column viewer**: dump every column of a `.csv` or `.xlsx` without loading it into your head.
- **Missing-value check**: count and ratio of nulls per column, the first thing to know about any new dataset.
- **Quick summary stats**: fast numeric summaries before any modeling.
- **CSV merger**: combine every CSV in a folder into one dataframe (the perennial task).
- **Column renamer**: clean and standardize messy column names.

## Why it earns its place

It's deliberately humble. The flagship projects get the attention, but reproducible research is built on exactly this kind of boring, reliable plumbing: the utilities you reach for every single day without thinking. Packaging them once, consistently, is itself a discipline: it's the smallest expression of the same scaffolding philosophy that runs through all my work.
