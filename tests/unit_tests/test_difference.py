"""
 Jason Herning
 03/02/2020
 test_differnce.py
 ---add summary---
"""


import pytest
import numpy as np

from scripts.difference import mask_difference




def test_mask_difference():

    x = np.array([[0, 0, 0, 0],
                  [1, 0, 0, 0],
                  [1, 1, 1, 0]])

    y = np.array([[0, 0, 0, 0],
                  [1, 1, 1, 1],
                  [1, 1, 1, 1]])

    t1 = mask_difference(x,y)

    out = np.array([[0, 0, 0, 0],
                    [0, 1, 1, 1],
                    [0, 0, 0, 1]])

    assert np.array_equal(t1, out), "Test failed"






