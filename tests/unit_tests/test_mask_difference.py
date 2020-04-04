"""
 Jason Herning
 03/02/2020
 test_differnce.py
 ---add summary---
"""


import pytest
import numpy as np

from scripts.mask_difference import water_added




def test_water_added():

    x = np.array([[0, 0, 1, 1],
                  [1, 0, 0, 0],
                  [1, 1, 1, 0]])

    y = np.array([[0, 0, 0, 0],
                  [1, 1, 1, 1],
                  [1, 1, 1, 1]])

    t1 = water_added(x,y)

    out = np.array([[0, 0, 2, 2],
                    [0, 1, 1, 1],
                    [0, 0, 0, 1]])

    assert np.array_equal(t1, out), "Test failed"





