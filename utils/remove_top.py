"""Remove the top percentage of values from an array.

Translates MATLAB ``remove_top.m``.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import ArrayLike


def remove_top(values: ArrayLike, threshold_percent: float) -> np.ndarray:
    """Sort *values* ascending and drop the top *threshold_percent* %.

    Parameters
    ----------
    values : array-like
        1-D collection of numeric values.
    threshold_percent : float
        Percentage of elements to remove from the top (0-100).

    Returns
    -------
    np.ndarray
        The remaining values after trimming, sorted ascending.
    """
    a = np.asarray(values, dtype=float).ravel()
    remove_n = math.floor(len(a) * threshold_percent / 100)
    a_sorted = np.sort(a)
    if remove_n == 0:
        return a_sorted
    return a_sorted[: len(a_sorted) - remove_n]
