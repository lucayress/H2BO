"""Build a homogeneity map image.

Translates MATLAB ``homog_map.m``.
"""

from __future__ import annotations

import numpy as np


def homog_map(
    data: np.ndarray,
    segments: np.ndarray,
    labels_homog: np.ndarray,
    labels_heter: np.ndarray,
) -> np.ndarray:
    """Create a 3-channel RGB image showing superpixel homogeneity.

    Homogeneous superpixels are painted white (1.0) and heterogeneous
    superpixels are painted gray (0.5).

    Parameters
    ----------
    data : np.ndarray
        Hyperspectral cube ``(rows, cols, bands)``.  Only its spatial
        dimensions are used; band values are overwritten.
    segments : np.ndarray
        2-D integer label map ``(rows, cols)``.
    labels_homog : np.ndarray
        Labels classified as homogeneous.
    labels_heter : np.ndarray
        Labels classified as heterogeneous.

    Returns
    -------
    np.ndarray
        RGB image ``(rows, cols, 3)`` with dtype ``float64``.
    """
    rows, cols = segments.shape
    rgb = np.zeros((rows, cols, 3), dtype=float)

    for label in labels_homog:
        mask = segments == label
        rgb[mask] = 1.0  # white

    for label in labels_heter:
        mask = segments == label
        rgb[mask] = 0.5  # gray

    return rgb
