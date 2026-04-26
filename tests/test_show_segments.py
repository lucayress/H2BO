"""Tests for utils.show_segments."""

import numpy as np
import pytest

from utils.show_segments import show_segments, DEFAULT_BANDS


class TestShowSegments:
    """Unit tests for show_segments."""

    def test_accepts_hyperspectral_cube(self):
        """Function runs on a channel-last hyperspectral cube."""
        rows, cols, bands = 10, 10, 50
        rng = np.random.RandomState(0)
        cube = rng.rand(rows, cols, bands)
        segments = np.zeros((rows, cols), dtype=int)

        result = show_segments(cube, segments)
        assert result.shape == (rows, cols, 3)

    def test_default_bands(self):
        """Default bands are the zero-based MATLAB equivalents."""
        assert DEFAULT_BANDS == (36, 15, 9)

    def test_custom_bands(self):
        """Custom band selection produces an image."""
        rows, cols, bands = 8, 8, 20
        rng = np.random.RandomState(1)
        cube = rng.rand(rows, cols, bands)
        segments = np.zeros((rows, cols), dtype=int)

        result = show_segments(cube, segments, bands=(0, 5, 10))
        assert result.shape == (rows, cols, 3)

    def test_output_range(self):
        """Output values should be in [0, 1]."""
        rows, cols, bands = 6, 6, 40
        rng = np.random.RandomState(2)
        cube = rng.rand(rows, cols, bands)
        segments = np.zeros((rows, cols), dtype=int)

        result = show_segments(cube, segments)
        assert result.min() >= 0.0
        assert result.max() <= 1.0
