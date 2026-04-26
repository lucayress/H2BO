"""Resegment heterogeneous superpixels with finer SLIC.

Translates MATLAB ``heter_segments.m`` using ``skimage.segmentation.slic``
with its native ``mask`` parameter instead of the fill-value workaround.
"""

from __future__ import annotations

from math import ceil

import numpy as np
from skimage.segmentation import slic


def _run_slic(
    image: np.ndarray,
    region_size: int,
    compactness: float,
    mask: np.ndarray | None = None,
) -> np.ndarray:
    """Internal SLIC wrapper used by both full-image and masked calls.

    Uses the VLFeat-style conversion from *region_size* to *n_segments*:

        n_segments = ceil(width / region_size) * ceil(height / region_size)

    For masked calls, the region size is applied to the crop dimensions
    and the ``mask`` is forwarded to ``skimage.segmentation.slic``.
    """
    h, w = image.shape[:2]
    n_segments = ceil(w / region_size) * ceil(h / region_size)
    # Ensure we request at least 1 segment
    n_segments = max(n_segments, 1)

    labels = slic(
        image,
        n_segments=n_segments,
        compactness=compactness,
        max_num_iter=100,
        sigma=0,
        convert2lab=False,
        enforce_connectivity=True,
        min_size_factor=1 / 36,
        start_label=0,
        mask=mask,
        channel_axis=-1,
    )
    return labels


def heter_segments(
    data: np.ndarray,
    segments: np.ndarray,
    labels_heter: np.ndarray,
    region_size: int,
    compactness: float,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Resegment heterogeneous superpixels at a finer SLIC scale.

    Parameters
    ----------
    data : np.ndarray
        Hyperspectral cube ``(rows, cols, bands)``.
    segments : np.ndarray
        Current 2-D integer label map.
    labels_heter : np.ndarray
        1-D array of labels to resegment.
    region_size : int
        SLIC region size for the finer scale.
    compactness : float
        SLIC compactness (regularisation) parameter.

    Returns
    -------
    new_segments : np.ndarray
        Updated label map with heterogeneous regions resegmented.
    labels : np.ndarray
        All unique labels in *new_segments*.
    num_superpixels : int
        Total number of superpixels after resegmentation.
    """
    segments = segments.copy()
    label_max = int(segments.max())

    for label in labels_heter:
        # Find bounding box of this superpixel
        rows, cols = np.where(segments == label)
        r_min, r_max = rows.min(), rows.max()
        c_min, c_max = cols.min(), cols.max()

        # Crop image and build boolean mask
        crop = data[r_min : r_max + 1, c_min : c_max + 1, :]
        sp_mask = segments[r_min : r_max + 1, c_min : c_max + 1] == label

        # Run masked SLIC on the crop
        sub_labels = _run_slic(crop, region_size, compactness, mask=sp_mask)

        # Remap valid labels (skip -1 = outside mask) into global space
        valid = sub_labels >= 0
        # Only write pixels that belong to the mask
        write_mask = valid & sp_mask

        # Offset sublabels so they are unique globally
        local = sub_labels[write_mask]
        # Re-number starting from label_max + 1
        unique_local = np.unique(local)
        remap = {v: label_max + 1 + idx for idx, v in enumerate(unique_local)}
        remapped = np.array([remap[v] for v in local])

        # Write back into global segmentation
        global_rows = rows  # already the absolute positions
        global_cols = cols
        # But we need the positions corresponding to write_mask
        wr, wc = np.where(write_mask)
        segments[wr + r_min, wc + c_min] = remapped

        label_max = int(segments.max())

    new_labels = np.unique(segments)
    return segments, new_labels, len(new_labels)
