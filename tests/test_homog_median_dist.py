"""Tests for utils.homog_median_dist."""

import numpy as np
import pytest

from utils.homog_median_dist import homog_median_dist


def _make_cube(rows, cols, bands, segments_map, spectra_dict):
    """Build a tiny hyperspectral cube from per-label spectra.

    Parameters
    ----------
    rows, cols, bands : int
        Cube dimensions.
    segments_map : np.ndarray
        (rows, cols) integer label map.
    spectra_dict : dict[int, np.ndarray]
        Mapping from label to (n_pixels, bands) spectra for that label.
        The arrays must have the correct number of pixels per label.

    Returns
    -------
    np.ndarray
        Cube with shape (rows, cols, bands).
    """
    cube = np.zeros((rows, cols, bands))
    for label, spectra in spectra_dict.items():
        mask = segments_map == label
        cube[mask] = spectra
    return cube


class TestHomogMedianDist:
    """Unit tests for homog_median_dist."""

    def test_known_homogeneous(self):
        """Constant spectrum gives ratio = 0 and is homogeneous."""
        rows, cols, bands = 4, 4, 5
        segments = np.zeros((rows, cols), dtype=int)
        cube = np.ones((rows, cols, bands)) * 3.0
        labels = np.array([0])

        lh, lhet, ratio = homog_median_dist(cube, segments, labels, 20, 10)

        assert len(lh) == 1
        assert len(lhet) == 0
        assert ratio[0] == pytest.approx(0.0)

    def test_known_heterogeneous(self):
        """Widely varying spectra give a high ratio and are heterogeneous."""
        rows, cols, bands = 4, 4, 5
        segments = np.zeros((rows, cols), dtype=int)

        # Give each pixel a very different spectrum so that
        # (max_trim - mean_trim) / mean_trim is large.
        rng = np.random.RandomState(99)
        cube = np.zeros((rows, cols, bands))
        # Most pixels are near 0, but a few are extreme outliers
        cube[:, :, :] = rng.rand(rows, cols, bands) * 0.01
        cube[0, 0, :] = 1000.0  # extreme outlier
        cube[3, 3, :] = 500.0   # another outlier

        labels = np.array([0])
        lh, lhet, ratio = homog_median_dist(cube, segments, labels, 20, 10)

        assert len(lhet) == 1
        assert len(lh) == 0
        assert ratio[0] > 20

    def test_nan_ratio_becomes_zero(self):
        """All-zero spectrum has an undefined raw ratio and should map to 0."""
        rows, cols, bands = 2, 2, 3
        segments = np.zeros((rows, cols), dtype=int)
        cube = np.zeros((rows, cols, bands))
        labels = np.array([0])

        lh, lhet, ratio = homog_median_dist(cube, segments, labels, 20, 10)
        assert ratio[0] == pytest.approx(0.0)

    def test_non_contiguous_labels(self):
        """Labels with gaps are handled correctly."""
        rows, cols, bands = 2, 4, 3
        segments = np.array([[0, 0, 5, 5],
                              [0, 0, 5, 5]])
        cube = np.ones((rows, cols, bands))
        labels = np.array([0, 5])  # non-contiguous

        lh, lhet, ratio = homog_median_dist(cube, segments, labels, 20, 10)
        assert len(lh) == 2
        assert len(ratio) == 2

    def test_verbose_prints(self, capsys):
        """verbose=True produces output."""
        rows, cols, bands = 2, 2, 3
        segments = np.zeros((rows, cols), dtype=int)
        cube = np.ones((rows, cols, bands))
        labels = np.array([0])

        homog_median_dist(cube, segments, labels, 20, 10, verbose=True)
        captured = capsys.readouterr()
        assert "num_sppx" in captured.out
