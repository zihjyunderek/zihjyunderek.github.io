"""Clustering tracts into archetypes, for the CDI-Clusters page.

Seven algorithms in three families, as in the project, on ACS indicators:
  numerical  K-Means, GMM, Ward           Yeo-Johnson features
  spatial    K-Medoids (FasterPAM)        robust-scaled features fused with distance on the ground
  density    DBSCAN, HDBSCAN, OPTICS      principal components of the Yeo-Johnson features

Archetypes are numbered by population density, densest first, in the
K-Medoids solution; every other solution is renumbered to overlap it as much
as possible, so "Archetype 1" means the same place in every view.
"""

from __future__ import annotations

import logging

import kmedoids
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN, HDBSCAN, OPTICS, AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import PowerTransformer, RobustScaler

from . import config
from .s01_indicators import complete, load_tracts

logger = logging.getLogger(__name__)

SLUG = "cdi-clusters"
INDICES = ("Silhouette", "Davies-Bouldin", "Calinski-Harabasz")


def features(tracts: pd.DataFrame) -> pd.DataFrame:
    """Return the clustering features under their figure labels, logged where configured."""
    out = pd.DataFrame(index=tracts.index)
    for column, (label, take_log) in config.ARCHETYPE_FEATURES.items():
        out[label] = np.log(tracts[column]) if take_log else tracts[column]
    return out


def fused_distance(robust: np.ndarray, coords: np.ndarray, weight: float) -> np.ndarray:
    """Blend feature distance with distance on the ground, each scaled to its own maximum."""
    by_feature = squareform(pdist(robust))
    by_ground = squareform(pdist(coords))
    return (1.0 - weight) * by_feature / by_feature.max() + weight * by_ground / by_ground.max()


def validity(space: np.ndarray, labels: np.ndarray, distance: np.ndarray | None = None) -> dict[str, float]:
    """Three validity indices; the silhouette uses the algorithm's own distance when it has one."""
    silhouette = silhouette_score(distance, labels, metric="precomputed") if distance is not None else silhouette_score(space, labels)
    return {
        "Silhouette": silhouette,
        "Davies-Bouldin": davies_bouldin_score(space, labels),
        "Calinski-Harabasz": calinski_harabasz_score(space, labels),
    }


def renumber(labels: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Relabel a solution so each cluster takes the number of the reference cluster it overlaps most."""
    table = pd.crosstab(labels, reference)
    rows, columns = linear_sum_assignment(-table.to_numpy())
    mapping = {table.index[r]: table.columns[c] for r, c in zip(rows, columns)}
    return np.array([mapping[label] for label in labels])


def by_density(labels: np.ndarray, density: pd.Series) -> np.ndarray:
    """Number clusters 1..K by median population density, densest first."""
    order = density.groupby(labels).median().sort_values(ascending=False).index
    rank = {label: i + 1 for i, label in enumerate(order)}
    return np.array([rank[label] for label in labels])


def signed(value: float) -> str:
    """Print a z-score with its sign and a typographic minus; plain 0.0 when it rounds to zero."""
    text = f"{value:+.1f}"
    return "0.0" if text in ("+0.0", "-0.0") else text.replace("-", "−")


def map_rows(tracts: pd.DataFrame, view_column: str, view: str, labels: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame({
        view_column: view,
        "geoid": tracts["geoid"].to_numpy(),  # maps find each tract's shape by GEOID
        "archetype": [f"Archetype {label}" for label in labels],
    })


def run() -> None:
    """Fit every algorithm, then write the validity grid, the maps, the medoids and the profiles."""
    tracts = complete(load_tracts(), list(config.ARCHETYPE_FEATURES))
    X = features(tracts)
    coords = tracts[["x_km", "y_km"]].to_numpy()
    power = PowerTransformer(method="yeo-johnson").fit_transform(X)
    robust = RobustScaler().fit_transform(X)
    seed, k_map = config.SEED, config.ARCHETYPE_K

    # ---- [Core Logic] numerical and spatial families, every K -------------
    fused = fused_distance(robust, coords, config.GEOGRAPHY_WEIGHT)
    fitters = {
        ("Numerical", "K-Means"): lambda k: KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(power),
        ("Numerical", "GMM"): lambda k: GaussianMixture(n_components=k, n_init=3, random_state=seed).fit_predict(power),
        ("Numerical", "Ward"): lambda k: AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(power),
        ("Spatial", "K-Medoids"): lambda k: kmedoids.fasterpam(fused, k, random_state=seed, n_cpu=1).labels,
    }
    grid: list[dict[str, str]] = []
    solutions: dict[str, np.ndarray] = {}
    for (family, algorithm), fit in fitters.items():
        for k in config.ARCHETYPE_K_RANGE:
            labels = np.asarray(fit(k))
            spatial = family == "Spatial"
            scores = validity(robust if spatial else power, labels, fused if spatial else None)
            for index in INDICES:
                decimals = 0 if index == "Calinski-Harabasz" else 2
                grid.append({"index": index, "family": family, "algorithm": algorithm, "k": f"K = {k}", "value": f"{scores[index]:.{decimals}f}"})
            if k == k_map:
                solutions[algorithm] = labels
        logger.info("  > %s fitted for K = %d..%d", algorithm, config.ARCHETYPE_K_RANGE[0], config.ARCHETYPE_K_RANGE[-1])

    reference = by_density(solutions["K-Medoids"], tracts["density"])
    aligned = {name: reference if name == "K-Medoids" else renumber(labels, reference) for name, labels in solutions.items()}

    # ---- [Core Logic] density family: K is found, not set ------------------
    components = PCA(n_components=config.DENSITY_COMPONENTS, random_state=seed).fit_transform(power)
    reach = NearestNeighbors(n_neighbors=config.DENSITY_MIN_SAMPLES).fit(components).kneighbors(components)[0][:, -1]
    density_fits = {
        "DBSCAN": DBSCAN(eps=float(np.quantile(reach, 0.9)), min_samples=config.DENSITY_MIN_SAMPLES).fit_predict(components),
        "HDBSCAN": HDBSCAN(min_cluster_size=config.HDBSCAN_MIN_CLUSTER, min_samples=config.DENSITY_MIN_SAMPLES, copy=True).fit_predict(components),
        "OPTICS": OPTICS(min_samples=config.DENSITY_MIN_SAMPLES, min_cluster_size=config.HDBSCAN_MIN_CLUSTER).fit_predict(components),
    }
    density_rows = []
    for algorithm, labels in density_fits.items():
        kept = labels >= 0
        found = len(set(labels[kept]))
        density_rows.append({
            "Algorithm": algorithm,
            "Clusters found": f"{found}",
            "Tracts left as noise": f"{100.0 * (~kept).mean():.0f}%",
            "Silhouette of the rest": f"{silhouette_score(components[kept], labels[kept]):.2f}" if found > 1 else "",
        })

    # ---- [Core Logic] how far the solutions agree at the mapped K ----------
    names = list(aligned)
    agreement = [{"Algorithm": a, **{b: ("" if a == b else f"{adjusted_rand_score(aligned[a], aligned[b]):.2f}") for b in names}} for a in names]

    out = config.FIGURE_DATA / SLUG
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(grid).to_csv(out / "validity.csv", index=False, lineterminator="\n")
    pd.DataFrame(density_rows).to_csv(out / "density_family.csv", index=False, lineterminator="\n")
    pd.DataFrame(agreement).to_csv(out / "agreement.csv", index=False, lineterminator="\n")
    pd.concat([map_rows(tracts, "algorithm", name, labels) for name, labels in aligned.items()]).to_csv(
        out / "archetype_map.csv", index=False, lineterminator="\n")
    logger.info("  > density family: %s", {r["Algorithm"]: (r["Clusters found"], r["Tracts left as noise"]) for r in density_rows})
    logger.info("  > agreement with K-Medoids (adjusted Rand): %s", {a["Algorithm"]: a["K-Medoids"] for a in agreement})

    # ---- [Core Logic] K-Medoids: geography weight, medoids, profiles -------
    views = []
    for name, weight in config.GEOGRAPHY_WEIGHTS.items():
        labels = kmedoids.fasterpam(fused_distance(robust, coords, weight), k_map, random_state=seed, n_cpu=1).labels
        views.append(map_rows(tracts, "distance", name, reference if weight == config.GEOGRAPHY_WEIGHT else renumber(np.asarray(labels), reference)))
    pd.concat(views).to_csv(out / "geography_map.csv", index=False, lineterminator="\n")

    result = kmedoids.fasterpam(fused, k_map, random_state=seed, n_cpu=1)
    number_of = dict(zip(result.labels, reference))  # raw cluster id -> archetype number
    medoid_rows = []
    for cluster, tract in sorted(enumerate(result.medoids), key=lambda pair: number_of[pair[0]]):
        row = tracts.iloc[tract]
        medoid_rows.append({
            "Archetype": f"Archetype {number_of[cluster]}",
            "Medoid tract": f"{str(row['tract_name']).split(';')[0].replace('Census Tract', 'Tract').strip()}, {row['borough']}",
            "Tracts": f"{int((reference == number_of[cluster]).sum()):,}",
            **{header: f"{row[column]:,.{decimals}f}" for column, (header, decimals) in config.MEDOID_COLUMNS.items()},
        })
    pd.DataFrame(medoid_rows).to_csv(out / "medoids.csv", index=False, lineterminator="\n")

    z = (X - X.mean()) / X.std()
    profile = z.groupby(reference).mean()
    long = [{"archetype": f"Archetype {number}", "feature": feature, "z": signed(profile.loc[number, feature])}
            for feature in X.columns for number in profile.index]
    pd.DataFrame(long).to_csv(out / "profiles.csv", index=False, lineterminator="\n")
    logger.info("  > archetype sizes: %s", pd.Series(reference).value_counts().sort_index().to_dict())
    logger.info("  > wrote %s/", SLUG)
