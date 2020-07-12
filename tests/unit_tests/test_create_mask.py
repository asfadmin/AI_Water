"""
 Jason Herning
 03/02/2020
 test_create_mask.py
 unit test for create_mask.py
"""

import numpy as np
import pytest

from scripts.create_mask import pad_image, get_tile_dimensions, tile_image


# tests for tile_image()
@pytest.mark.parametrize("input_shape, output_shape", [((2048, 2048), (16, 512, 512)),
                                                       ((8192, 8192), (256, 512, 512))])
def test_tile_image_shape(input_shape, output_shape):
    input = tile_image(np.eye(*input_shape)).shape
    expected = output_shape
    assert input == expected, f"{input} != {expected}"
