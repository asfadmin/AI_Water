"""
 Jason Herning
 03/02/2020
 test_mask_difference.py
 unit test for mask_difference.py
"""
import numpy as np
import pytest

from scripts.mask_difference import difference

# test bank

# Test 1
test_1_lin = np.array([[0, 0, 1, 1],
                       [1, 0, 0, 0],
                       [1, 1, 1, 0]])

test_1_rin = np.array([[0, 0, 0, 0],
                       [1, 1, 1, 1],
                       [1, 1, 1, 1]])

test_1_out = np.array([[0, 0, 2, 2],
                       [0, 1, 1, 1],
                       [0, 0, 0, 1]])

# Test 2
test_2_lin = np.array([[0, 0],
                       [0, 0]])

test_2_rin = np.array([[1, 1],
                       [1, 1]])

test_2_out = np.array([[1, 1],
                       [1, 1]])


@pytest.mark.parametrize("diff, out", [(difference(test_1_lin, test_1_rin), test_1_out),
                                       (difference(test_2_lin, test_2_rin), test_2_out)])
def test_mask_difference(diff, out):
    assert np.array_equal(diff, out), "Test failed"
