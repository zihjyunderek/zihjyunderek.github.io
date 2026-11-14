"""An exclusion index on ACS proxies, for the City-Indices page.

The USEI itself rests on access metrics that are confidential. This stage
shows the same construction on public data: choose components, put them on
one scale, weight them, and check that the ranking survives other choices.

Recipe: clip each component to its 1st-99th percentile, rescale to 0-100
(higher = more excluded), average the components of a dimension, then average
the dimensions.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA

from . import config
from .s01_indicators import complete, load_tracts

logger = logging.getLogger(__name__)

SLUG = "city-indices"


def scaled(values: pd.DataFrame) -> pd.DataFrame:
    """Clip every column to the winsor percentiles and rescale it to 0-100."""
    low, high = values.quantile(config.EXCLUSION_WINSOR[0]), values.quantile(config.EXCLUSION_WINSOR[1])
    return 100.0 * (values.clip(low, high, axis=1) - low) / (high - low)


def by_dimension(components: pd.DataFrame) -> pd.DataFrame:
    """Average the components of each dimension."""
    dimension = {name: dim for name, dim, _ in config.EXCLUSION_COMPONENTS.values()}
    return components.T.groupby(dimension, sort=False).mean().T


def alternatives(raw: pd.DataFrame, components: pd.DataFrame) -> dict[str, pd.Series]:
    """Rebuild the index under other reasonable choices, to test the ranking."""
    zscores = (raw - raw.mean()) / raw.std()
    ranks = raw.rank(pct=True) * 100.0
    loadings = np.abs(PCA(n_components=1, random_state=config.SEED).fit(zscores).components_[0])
    dimensions = by_dimension(components)
    out = {
        "Z-scores, not 0–100": by_dimension(zscores).mean(axis=1),
        "Percentile ranks": by_dimension(ranks).mean(axis=1),
        "Weights from PCA": components.mul(loadings / loadings.sum(), axis=1).sum(axis=1),
        "Geometric mean": np.exp(np.log(dimensions + 1.0).mean(axis=1)) - 1.0,
    }
    for dropped in dimensions.columns:
        out[f"Without {dropped.lower()}"] = dimensions.drop(columns=dropped).mean(axis=1)
    return out


def run() -> None:
    """Write the component table, the mapped scores, borough means, and the robustness check."""
    tracts = load_tracts()
    tracts["no_college_share"] = 100.0 - tracts["college_share"]
    tracts = complete(tracts, list(config.EXCLUSION_COMPONENTS))
    labels = {column: name for column, (name, _, _) in config.EXCLUSION_COMPONENTS.items()}
    raw = tracts[list(labels)].rename(columns=labels)
    components = scaled(raw)
    dimensions = by_dimension(components)
    index = dimensions.mean(axis=1).rename(config.INDEX_LABEL)

    out = config.FIGURE_DATA / SLUG
    out.mkdir(parents=True, exist_ok=True)

    per_dimension = pd.Series({name: dim for name, dim, _ in config.EXCLUSION_COMPONENTS.values()}).value_counts()
    table = [{
        "Dimension": dim, "Component": name, "ACS table": source,
        "Weight in the index": f"{100.0 / len(per_dimension) / per_dimension[dim]:.1f}%",
    } for name, dim, source in config.EXCLUSION_COMPONENTS.values()]
    pd.DataFrame(table).to_csv(out / "components.csv", index=False, lineterminator="\n")

    views = pd.concat([index, dimensions], axis=1)
    # maps find each tract's shape by GEOID
    mapped = [pd.DataFrame({"view": view, "geoid": tracts["geoid"].to_numpy(), "score": views[view].map("{:.0f}".format).to_numpy()})
              for view in views.columns]
    pd.concat(mapped).to_csv(out / "index_map.csv", index=False, lineterminator="\n")

    scores = pd.concat([index, components], axis=1)
    boroughs = scores.groupby(tracts["borough"]).mean().sort_values(config.INDEX_LABEL, ascending=False)
    dimension_of = {config.INDEX_LABEL: "Composite", **{name: dim for name, dim, _ in config.EXCLUSION_COMPONENTS.values()}}
    profile = [{"dimension": dimension_of[measure], "measure": measure, "borough": borough, "score": f"{boroughs.loc[borough, measure]:.0f}"}
               for measure in boroughs.columns for borough in boroughs.index]
    pd.DataFrame(profile).to_csv(out / "borough_profile.csv", index=False, lineterminator="\n")

    checks = [{"scheme": name, "rank_correlation": f"{spearmanr(index, other).statistic:.3f}"}
              for name, other in alternatives(raw, components).items()]
    pd.DataFrame(checks).to_csv(out / "robustness.csv", index=False, lineterminator="\n")

    logger.info("  > index: mean %.1f, range %.0f-%.0f over %d tracts", index.mean(), index.min(), index.max(), len(index))
    logger.info("  > borough means: %s", boroughs[config.INDEX_LABEL].round(1).to_dict())
    logger.info("  > rank correlation with the baseline: %s", {c["scheme"]: c["rank_correlation"] for c in checks})
    logger.info("  > wrote %s/components.csv, index_map.csv, borough_profile.csv, robustness.csv", SLUG)
