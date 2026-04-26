"""Tests for utils.remove_top."""

import numpy as np
import pytest

from utils.remove_top import remove_top


class TestRemoveTop:
    """Unit tests for remove_top."""

    def test_no_trimming(self):
        """threshold=0 removes no elements."""
        vals = [5, 3, 1, 4, 2]
        result = remove_top(vals, 0)
        np.testing.assert_array_equal(result, [1, 2, 3, 4, 5])

    def test_partial_trimming(self):
        """Remove the top 20% of 10 elements, dropping 2."""
        vals = np.arange(1, 11, dtype=float)  # 1..10
        result = remove_top(vals, 20)
        # floor(10 * 20 / 100) = 2, keep 1..8
        np.testing.assert_array_equal(result, np.arange(1, 9, dtype=float))

    def test_small_array(self):
        """Single-element array with threshold < 100 keeps the element."""
        result = remove_top([42.0], 10)
        np.testing.assert_array_equal(result, [42.0])

    def test_threshold_removes_zero(self):
        """Low threshold on a small array rounds to zero removals."""
        vals = [10, 20, 30]
        # floor(3 * 5 / 100) = floor(0.15) = 0, nothing removed
        result = remove_top(vals, 5)
        np.testing.assert_array_equal(result, [10, 20, 30])

    def test_full_removal(self):
        """threshold=100 removes all elements."""
        vals = [1, 2, 3]
        # floor(3 * 100 / 100) = 3, empty
        result = remove_top(vals, 100)
        assert len(result) == 0

    def test_result_is_sorted_ascending(self):
        """Output is always sorted ascending."""
        vals = [9, 1, 5, 3, 7]
        result = remove_top(vals, 20)  # remove 1
        assert list(result) == sorted(result)
