"""OLS, GWR and MGWR on public ACS data, for the Multiscale-GWR page.

Question: what goes with a tract's median rent, and over what distance does
each relationship hold? Variables enter by forward selection on GWR's AICc,
the final set is fitted three ways, and each fit is checked for spatial
autocorrelation left in its residuals.

Every variable is standardized, so coefficients are in standard deviations
of log rent per standard deviation of the predictor. Kernel: adaptive
bisquare; a bandwidth is a number of nearest tracts.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from esda.moran import Moran
from libpysal.weights import KNN
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
from spglm.family import Gaussian
from spglm.glm import GLM

from . import config
from .s01_indicators import complete, load_tracts

logger = logging.getLogger(__name__)

SLUG = "multiscale-gwr"


def standardized(tracts: pd.DataFrame, column: str, take_log: bool) -> np.ndarray:
    """Return one column as z-scores, logged first when configured."""
    values = np.log(tracts[column]) if take_log else tracts[column]
    return ((values - values.mean()) / values.std()).to_numpy().reshape(-1, 1)


def forward_selection(coords: np.ndarray, y: np.ndarray, pool: dict[str, np.ndarray]) -> tuple[list[str], list[dict[str, str]]]:
    """Add, one at a time, the candidate that lowers GWR's AICc the most."""
    chosen: list[str] = []
    steps: list[dict[str, str]] = []
    best = np.inf
    while len(chosen) < config.STEPWISE_MAX_TERMS:
        trials = {}
        for name in pool:
            if name in chosen:
                continue
            X = np.hstack([pool[term] for term in [*chosen, name]])
            bandwidth = Sel_BW(coords, y, X).search()
            trials[name] = (GWR(coords, y, X, bandwidth).fit(), bandwidth)
        name, (fit, bandwidth) = min(trials.items(), key=lambda item: item[1][0].aicc)
        if best - fit.aicc < config.STEPWISE_MIN_GAIN:
            logger.info("  > forward selection stops: %s would lower AICc by %.1f only", name, best - fit.aicc)
            break
        chosen.append(name)
        best = fit.aicc
        steps.append({"step": f"{len(chosen)}. {name}", "aicc": f"{fit.aicc:.0f}", "adj_r2": f"{fit.adj_R2:.3f}", "bandwidth": f"{int(bandwidth)}"})
        logger.info("  > step %d: + %s, AICc %.0f, adjusted R2 %.3f, bandwidth %d", len(chosen), name, fit.aicc, fit.adj_R2, bandwidth)
    return chosen, steps


def minus(text: str) -> str:
    """Print a negative number with a typographic minus, as a table should."""
    return text.replace("-", "−")


def morans_i(residuals: np.ndarray, weights: KNN) -> Moran:
    """Moran's I of a model's residuals on the nearest-neighbour graph, by permutation."""
    np.random.seed(config.SEED)  # esda draws its permutations from numpy's global state
    return Moran(residuals.flatten(), weights, permutations=config.MORAN_PERMUTATIONS)


def variance_inflation(X: np.ndarray) -> np.ndarray:
    """VIF of each column: 1 / (1 - R2) from regressing it on the others."""
    return np.diag(np.linalg.inv(np.corrcoef(X, rowvar=False)))


def run() -> None:
    """Select variables, fit the three models, and write every CSV the page draws."""
    target, _, target_log = config.MGWR_TARGET
    tracts = complete(load_tracts(), [target, *config.MGWR_CANDIDATES])
    coords = tracts[["x_km", "y_km"]].to_numpy()
    y = standardized(tracts, target, target_log)
    pool = {label: standardized(tracts, column, take_log) for column, (label, take_log) in config.MGWR_CANDIDATES.items()}

    # ---- [Core Logic] which variables ------------------------------------
    terms, steps = forward_selection(coords, y, pool)
    X = np.hstack([pool[term] for term in terms])
    names = [config.INTERCEPT_LABEL, *terms]

    # ---- [Core Logic] three models on the same variables -----------------
    ols = GLM(y, X, family=Gaussian(), constant=True).fit()
    n, k = X.shape
    ols_aicc = ols.aic + 2.0 * (k + 2) * (k + 3) / (n - k - 3)  # small-sample correction, k + 2 parameters
    ols_adj_r2 = 1.0 - (1.0 - ols.D2) * (n - 1) / (n - k - 1)

    gwr_bandwidth = Sel_BW(coords, y, X).search()
    gwr = GWR(coords, y, X, gwr_bandwidth).fit()
    logger.info("  > GWR: bandwidth %d, AICc %.0f, adjusted R2 %.3f", gwr_bandwidth, gwr.aicc, gwr.adj_R2)

    selector = Sel_BW(coords, y, X, multi=True)
    bandwidths = selector.search()
    mgwr = MGWR(coords, y, X, selector).fit()
    logger.info("  > MGWR: bandwidths %s, AICc %.0f, adjusted R2 %.3f", {name: int(value) for name, value in zip(names, bandwidths)}, mgwr.aicc, mgwr.adj_R2)

    # islands and peninsulas make the nearest-neighbour graph fall into separate parts; Moran's I does not need it connected
    weights = KNN.from_array(coords, k=config.MORAN_NEIGHBOURS, silence_warnings=True)
    weights.transform = "r"
    residuals = {"OLS": ols.resid_response, "GWR": gwr.resid_response, "MGWR": mgwr.resid_response}
    moran = {model: morans_i(values, weights) for model, values in residuals.items()}

    geoid = tracts["geoid"].to_numpy()  # maps find each tract's shape by GEOID

    # ---- [Core Logic] models, bandwidths and coefficients ----------------
    out = config.FIGURE_DATA / SLUG
    out.mkdir(parents=True, exist_ok=True)
    scale = [{"term": name, "model": model, "neighbours": f"{int(value)}"}
             for name, value in zip(names, bandwidths) for model, value in (("GWR", gwr_bandwidth), ("MGWR", value))]
    pd.DataFrame(scale).to_csv(out / "bandwidths.csv", index=False, lineterminator="\n")

    significant = mgwr.filter_tvals()  # t-values, zero where not significant after the multiple-testing correction
    surfaces = [pd.DataFrame({
        "term": name, "geoid": geoid,
        "coefficient": [f"{value:.2f}" if keep else "" for value, keep in zip(mgwr.params[:, j], significant[:, j] != 0)],
    }) for j, name in enumerate(names) if j > 0]
    pd.concat(surfaces).to_csv(out / "coefficients.csv", index=False, lineterminator="\n")

    def left_over(model: str) -> dict[str, str]:
        """Moran's I of a model's residuals and its permutation p-value, as printed."""
        p = moran[model].p_sim
        return {"Residual Moran's I": minus(f"{moran[model].I:.3f}"), "p": "<0.001" if p < 0.001 else f"{p:.3f}"}

    def row(model: str, adj_r2: float, aicc: float, enp: float) -> dict[str, str]:
        return {"Model": model, "Adjusted R²": f"{adj_r2:.3f}", "AICc": f"{aicc:,.0f}",
                "ENP": f"{enp:.0f}", **left_over(model)}
    comparison = [
        row("OLS", ols_adj_r2, ols_aicc, k + 1),
        row("GWR", gwr.adj_R2, gwr.aicc, gwr.ENP),
        row("MGWR", mgwr.adj_R2, mgwr.aicc, mgwr.ENP),
    ]
    pd.DataFrame(comparison).to_csv(out / "model_comparison.csv", index=False, lineterminator="\n")

    # ---- [Core Logic] selection, diagnostics and residuals ----------------
    pd.DataFrame(steps).to_csv(out / "forward_selection.csv", index=False, lineterminator="\n")

    spread = {model: values.flatten() / values.std() for model, values in residuals.items()}
    pd.concat([pd.DataFrame({"model": model, "geoid": geoid, "residual": [f"{v:.2f}" for v in np.clip(values, -3.0, 3.0)]})
               for model, values in spread.items()]).to_csv(out / "residuals.csv", index=False, lineterminator="\n")


    local_vif = gwr.local_collinearity()[1]  # one column per predictor
    share = (significant != 0).mean(axis=0) * 100.0
    diagnostics = [{
        "Term": name,
        "Global VIF": f"{variance_inflation(X)[j - 1]:.2f}" if j else "",
        "Largest local VIF": f"{local_vif[:, j - 1].max():.2f}" if j else "",
        "MGWR bandwidth": f"{int(bandwidths[j]):,}",
        "Tracts with a significant estimate": f"{share[j]:.0f}%",
    } for j, name in enumerate(names)]
    pd.DataFrame(diagnostics).to_csv(out / "diagnostics.csv", index=False, lineterminator="\n")

    logger.info("  > residual Moran's I: %s", {model: round(float(m.I), 3) for model, m in moran.items()})
    logger.info("  > share of tracts significant, %%: %s", {name: int(round(value)) for name, value in zip(names, share)})
    logger.info("  > wrote %s/ (%d tracts)", SLUG, n)
