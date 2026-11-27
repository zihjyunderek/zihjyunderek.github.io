"""Simulated illustration for the CDI-Survey page.

The real scores are confidential and no public survey has the same structure,
so this stage simulates files shaped like the delivered ones and then repeats
the two steps of the project on them: test candidate structures against the
delivered composite, and verify the recovered one city by city.

Structure being recovered: per travel mode, a mode score is the mean of a
four-question battery of tract means; the composite is the sum of the mode
scores weighted by each tract's travel-mode shares.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import config

logger = logging.getLogger(__name__)

SLUG = "cdi-survey"
RECOVERED = "Tract weights, mean"  # the structure the project recovered


def simulate_city(rng: np.random.Generator, tracts: int) -> dict[str, np.ndarray]:
    """Return one city's delivered files: question means, mode weights, composite."""
    modes = len(config.SATISFACTION_MODES)
    level = rng.normal(3.4, 0.35, size=(tracts, 1, 1))  # a tract's general mood
    mode_shift = rng.normal(0.0, 0.45, size=(tracts, modes, 1))  # how it feels about each mode
    questions = np.clip(level + mode_shift + rng.normal(0.0, 0.3, size=(tracts, modes, config.SATISFACTION_QUESTIONS)), 1.0, 5.0)
    weights = rng.dirichlet(alpha=(4.0, 1.5, 2.5), size=tracts)
    composite = (weights * questions.mean(axis=2)).sum(axis=1)
    decimals = config.SATISFACTION_DECIMALS
    return {
        "questions": questions.round(decimals),
        "weights": weights.round(decimals),
        "composite": composite.round(decimals),
    }


def candidates(city: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Rebuild the composite from the delivered inputs under each candidate structure.

    A mode score is the mean or the median of its four questions; the three
    mode scores are then averaged plainly, or weighted by mode shares taken
    city-wide or tract by tract.
    """
    questions, weights = city["questions"], city["weights"]
    mean_score = questions.mean(axis=2)
    return {
        "Plain mean": mean_score.mean(axis=1),
        "City-wide weights": mean_score @ weights.mean(axis=0),
        "Tract weights, median": (weights * np.median(questions, axis=2)).sum(axis=1),
        RECOVERED: (weights * mean_score).sum(axis=1),
    }


def rounding_bound(city: dict[str, np.ndarray]) -> np.ndarray:
    """Largest error rounding alone can cause, tract by tract.

    Every delivered number is off by at most half a unit of its last decimal.
    That error enters three times: through the weights (times the mode scores),
    through the mode scores (times weights that sum to one), and through the
    delivered composite itself.
    """
    half_unit = 0.5 * 10.0 ** -config.SATISFACTION_DECIMALS
    return half_unit * (city["questions"].mean(axis=2).sum(axis=1) + 2.0)


def run() -> None:
    """Write the candidate-structure errors and the per-city verification table."""
    rng = np.random.default_rng(config.SEED)
    errors: list[dict[str, str]] = []
    checks: list[dict[str, str]] = []
    for name, tracts in config.SATISFACTION_CITIES.items():
        city = simulate_city(rng, tracts)
        rebuilt = candidates(city)
        for structure, values in rebuilt.items():
            gap = np.abs(values - city["composite"])
            errors.append({"structure": structure, "city": name, "max_abs_error": f"{gap.max():.6f}"})
        gap = np.abs(rebuilt[RECOVERED] - city["composite"])
        bound = rounding_bound(city)
        checks.append({
            "City": name,
            "Tracts": f"{tracts}",
            "Largest error": f"{gap.max():.6f}",
            "Rounding bound": f"{bound.max():.6f}",
            "Within bound": "Yes" if (gap <= bound).all() else "No",
        })
        logger.info("  > %s: %d tracts, largest error of the recovered structure %.2e", name, tracts, gap.max())

    out = config.FIGURE_DATA / SLUG
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(errors).to_csv(out / "structure_errors.csv", index=False, lineterminator="\n")
    pd.DataFrame(checks).to_csv(out / "verification.csv", index=False, lineterminator="\n")
    logger.info("  > wrote %s/structure_errors.csv and verification.csv", SLUG)
