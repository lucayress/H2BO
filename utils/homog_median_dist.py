"""Homogeneity test based on the median spectral distance.

Translates MATLAB ``homog_median_dist.m``.
"""

from __future__ import annotations

import numpy as np

from .remove_top import remove_top


def homog_median_dist(
    data: np.ndarray,
    segments: np.ndarray,
    labels: np.ndarray,
    tau_homog: float,
    tau_outliers: float,
    verbose: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Classify superpixels as homogeneous or heterogeneous.

    For each label the function computes a distance ratio between the
    trimmed-max and trimmed-mean Euclidean distance of every pixel
    spectrum to the superpixel's median spectrum.

    Parameters
    ----------
    data : np.ndarray
        Hyperspectral cube with shape ``(rows, cols, bands)``.
    segments : np.ndarray
        2-D integer label map with shape ``(rows, cols)``.
    labels : np.ndarray
        1-D array of label values to test.
    tau_homog : float
        Distance-ratio threshold; labels with ratio <= *tau_homog* are
        classified as homogeneous.
    tau_outliers : float
        Percentage of top distances to trim before computing the ratio.
    verbose : bool, optional
        If ``True``, print superpixel counts.

    Returns
    -------
    labels_homog : np.ndarray
        Labels classified as homogeneous.
    labels_heter : np.ndarray
        Labels classified as heterogeneous.
    dist_ratio : np.ndarray
        Distance ratio for each label (same length as *labels*).
    """
    rows, cols, bands = data.shape
    n_pixels = rows * cols
    im_2d = data.reshape(n_pixels, bands)  # (N, L)

    num_sp = len(labels)
    dist_ratio = np.zeros(num_sp)

    for i, label in enumerate(labels):
        mask = segments == label
        sp_pixels = im_2d[mask.ravel()]  # (n_pix, L)

        sp_median = np.median(sp_pixels, axis=0)  # (L,)
        diffs = sp_pixels - sp_median  # (n_pix, L)
        sp_dist = np.sqrt(np.sum(diffs ** 2, axis=1))  # (n_pix,)

        trimmed = remove_top(sp_dist, tau_outliers)
        if len(trimmed) == 0:
            dist_ratio[i] = 0.0
            continue

        avg_trim = np.mean(trimmed)
        max_trim = np.max(trimmed)

        if avg_trim == 0:
            ratio = 0.0
        else:
            ratio = 100.0 * (max_trim - avg_trim) / avg_trim

        dist_ratio[i] = 0.0 if np.isnan(ratio) else ratio

    homog_mask = dist_ratio <= tau_homog
    labels_homog = labels[homog_mask]
    labels_heter = labels[~homog_mask]

    if verbose:
        print(f"num_sppx\t  = {num_sp}")
        print(f"heter_sppx\t  = {len(labels_heter)}")
        print(f"homog_sppx\t  = {len(labels_homog)}")

    return labels_homog, labels_heter, dist_ratio
