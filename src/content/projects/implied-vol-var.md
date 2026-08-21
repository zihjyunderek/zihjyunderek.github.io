---
title: "Option-Implied VaR for G7 Currencies"
tagline: "Master's thesis (NCCU, 2026): forecasting FX spot Value-at-Risk from option-implied volatilities with quantile regression and machine learning, across the G7 currency pairs."
domain: finance
stack: ["Python", "Quantile Regression", "CatBoost", "Docker"]
stats:
  - { value: "G7", label: "currency pairs" }
  - { value: "VaR", label: "risk forecasting" }
  - { value: "QR + ML", label: "dual approach" }
featured: true
order: 2
repo: "https://github.com/zihjyunderek/G7_VaR"
status: research
---

My master's thesis at NCCU Money and Banking (M.S., 2026): *Forecasting FX Spot Value-at-Risk (VaR) Using Implied Volatility: Evidence from G7 Currency Pairs*. It bridges the two halves of my background: market-risk practice from CTBC and Foxconn treasury internships, and the statistical modeling I use daily. The question is deceptively simple: **can the market's own forward-looking view of volatility predict tomorrow's downside risk better than history can?**

## The idea

Traditional Value-at-Risk looks backward: it estimates how bad a loss could be from the distribution of past returns. But option prices encode the market's *forward* expectation of volatility. This project extracts implied volatilities from FX option chains and uses them as predictors of spot-rate VaR, comparing two estimation philosophies:

- **Quantile Regression**: models the conditional tail directly, no distributional assumption about returns. You estimate the 1% or 5% quantile as a function of implied vol, rather than estimating a whole distribution and reading off its tail.
- **Machine Learning (gradient-boosted trees)**: captures nonlinear, regime-dependent relationships between the implied-vol surface and realized tail risk that a linear quantile model would miss.

## Why it matters

Implied volatility is a leading indicator; realized volatility is a lagging one. A VaR model fed by implied vol can react to a brewing crisis *before* it shows up in the return history, exactly when a risk desk most needs the warning. The project benchmarks implied-vol-driven VaR against classical historical and parametric approaches across all G7 crosses, then backtests coverage with standard exception tests.

## Engineering

The full pipeline is containerized (`Dockerfile` plus `docker-compose`) with a config-driven runner (`run_configs.py`) that sweeps currency pairs and model specifications reproducibly. The literature base (Estimating VaR from implied volatilities; backtesting VaR models) is version-controlled alongside the code, so the theory and the implementation never drift apart. The complete implementation lives in the [G7_VaR repository](https://github.com/zihjyunderek/G7_VaR) on GitHub.
