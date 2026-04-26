"""Visualise superpixel boundaries on a false-colour image.

Translates MATLAB ``show_segments.m`` using skimage boundary detection.
"""

from __future__ import annotations

import numpy as np
from skimage.segmentation import mark_boundaries


# MATLAB demo bands [37, 16, 10] converted to Python 0-based [36, 15, 9].
DEFAULT_BANDS = (36, 15, 9)


def show_segments(
    data: np.ndarray,
    segments: np.ndarray,
    bands: tuple[int, ...] = DEFAULT_BANDS,
) -> np.ndarray:
    """Return a false-colour RGB image with superpixel boundaries overlaid.

    Parameters
    ----------
    data : np.ndarray
        Hyperspectral cube ``(rows, cols, bands_total)``.
    segments : np.ndarray
        2-D integer label map ``(rows, cols)``.
    bands : tuple of int, optional
        Three zero-based band indices for false-colour RGB.
        Defaults to ``(36, 15, 9)`` (the MATLAB demo selection
        converted to 0-based).

    Returns
    -------
    np.ndarray
        RGB image ``(rows, cols, 3)`` with dtype ``float64``,
        boundaries drawn in black.
    """
    # Select bands and normalise to [0, 1]
    img_color = data[:, :, list(bands)].astype(float)
    lo = img_color.min()
    hi = img_color.max()
    if hi - lo > 0:
        img_color = (img_color - lo) / (hi - lo)
    else:
        img_color = np.zeros_like(img_color)

    # Overlay single-pixel boundaries.
    marked = mark_boundaries(img_color, segments, color=(0, 0, 0), mode="inner")
    return marked
