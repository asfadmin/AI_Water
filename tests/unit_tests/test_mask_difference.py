"""
 Jason Herning
 03/02/2020
 test_mask_difference.py
 unit test for mask_difference.py
"""
import numpy as np

from scripts.mask_difference import difference


def test_difference():
    x = np.array([[0, 0, 1, 1],
                  [1, 0, 0, 0],
                  [1, 1, 1, 0]])

    y = np.array([[0, 0, 0, 0],
                  [1, 1, 1, 1],
                  [1, 1, 1, 1]])

    t1 = difference(x, y)

    out = np.array([[0, 0, 2, 2],
                    [0, 1, 1, 1],
                    [0, 0, 0, 1]])

    assert np.array_equal(t1, out), "Test failed"
