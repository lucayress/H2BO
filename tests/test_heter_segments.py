"""Tests for utils.heter_segments."""

import numpy as np
import pytest

from utils.heter_segments import heter_segments


class TestHeterSegments:
    """Unit tests for heter_segments."""

    def test_global_labels_unique(self):
        """After resegmentation, all labels in the map are unique."""
        rows, cols, bands = 8, 8, 10
        rng = np.random.RandomState(42)
        cube = rng.rand(rows, cols, bands)

        # Two superpixels: left half = 0, right half = 1
        segments = np.zeros((rows, cols), dtype=int)
        segments[:, 4:] = 1

        labels_heter = np.array([1])

        new_seg, new_labels, n_sp = heter_segments(
            cube, segments, labels_heter, region_size=3, compactness=0.00225,
        )

        # Labels should be unique
        assert len(new_labels) == len(np.unique(new_seg))
        # Original label 0 should still exist
        assert 0 in new_labels

    def test_unchanged_pixels_preserved(self):
        """Pixels outside heterogeneous regions keep their original label."""
        rows, cols, bands = 8, 8, 10
        rng = np.random.RandomState(42)
        cube = rng.rand(rows, cols, bands)

        segments = np.zeros((rows, cols), dtype=int)
        segments[:, 4:] = 1

        labels_heter = np.array([1])

        new_seg, _, _ = heter_segments(
            cube, segments, labels_heter, region_size=3, compactness=0.00225,
        )

        # Left half should be untouched (label 0)
        np.testing.assert_array_equal(new_seg[:, :4], 0)

    def test_mask_ignores_outside(self):
        """Masked SLIC should not produce label -1 in the output."""
        rows, cols, bands = 10, 10, 5
        rng = np.random.RandomState(7)
        cube = rng.rand(rows, cols, bands)

        # Create a single superpixel that is not a full rectangle
        segments = np.zeros((rows, cols), dtype=int)
        segments[2:8, 2:8] = 1  # inner block

        labels_heter = np.array([1])

        new_seg, _, _ = heter_segments(
            cube, segments, labels_heter, region_size=2, compactness=0.00225,
        )

        assert -1 not in new_seg
        # Label 0 border should be preserved
        assert new_seg[0, 0] == 0
