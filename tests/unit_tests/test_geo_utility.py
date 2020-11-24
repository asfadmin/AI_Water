"""
 Created By:   Jason Herning
 Date Created: 09-21-2020
 File Name:    test_geo_utility.py
 Description:  unit test for functions from geo_utility.py
"""

import numpy as np
import pytest
from src.geo_utility import pad_image, get_tile_dimensions, stride_tile_image


# tests for tile_image()
@pytest.mark.parametrize("input_shape, output_shape", [((2048, 2048), (16, 512, 512)),
                                                       ((8192, 8192), (256, 512, 512))])
def test_stride_tile_image_shape(input_shape, output_shape):
    input = stride_tile_image(np.eye(*input_shape)).shape
    expected = output_shape
    assert input == expected, f"{input} != {expected}"


# tests for pad_image()
def test_pad_image_shape():
    """Comparing shape of the np.ndarray returned by pad_image"""
    input = pad_image(np.eye(2000, 2000), 512).shape
    expected = np.eye(2048, 2048).shape
    assert input == expected, f"shape does not match | {input.shape} != {expected.shape}"


# tests for get_tile_dimensions()
def test_get_tile_dimensions():
    """Compare dimensions returned"""
    input = get_tile_dimensions(2000, 2000, 512)
    expected = (4, 4)
    assert input == expected, "dimensions do not match"
