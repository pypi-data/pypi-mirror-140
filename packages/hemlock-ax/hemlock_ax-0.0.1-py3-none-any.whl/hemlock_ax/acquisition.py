"""Acquisition functions.
"""
from __future__ import annotations

from typing import Callable, Dict

import numpy as np


def thompson(samples: np.ndarray) -> np.ndarray:
    """Thompson sampling.

    Args:
        samples (np.ndarray): (n sample, n arms) array of samples from a distribution
            of effects.

    Returns:
        np.ndarray: (n arms,) array of assignment weights.
    """
    return np.identity(samples.shape[1])[samples.argmax(axis=1)].mean(axis=0)


def exploration(samples: np.ndarray) -> np.ndarray:
    """Exploration sampling.

    Args:
        samples (np.ndarray): (n sample, n arms) array of samples from a distribution
            of effects.

    Returns:
        np.ndarray: (n arms,) array of assignment weights.
    """
    weights = thompson(samples)
    return weights * (1 - weights)


functions: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "exploration": exploration,
    "thompson": thompson,
}
