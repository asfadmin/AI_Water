"""
 Jason Herning
 03/02/2020
 test_mask_difference.py
 unit test for mask_difference.py
"""
import numpy as np
import pytest

from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly

from scripts.mask_difference import difference, intersection

path_dataset = "tests/unit_tests/dataset/"


@pytest.fixture
def supply_intersection():
    raster1_path = path_dataset + "difference_kodiak_spring"
    raster2_path = path_dataset + "difference_kodiak_summer"

    raster1 = gdal.Open(raster1_path, GA_ReadOnly)
    raster2 = gdal.Open(raster2_path, GA_ReadOnly)

    # for x in intersection(raster1, raster2): print(f"======{x}")

    return intersection(raster1_path, raster2_path)


def test_intersection_array1(supply_intersection):
    array1 = np.load(path_dataset + "intersect_kodiak_spring.npy")
    assert np.array_equal(supply_intersection[0], array1), "array1 intersections do not match"


def test_intersection_array2(supply_intersection):
    array2 = np.load(path_dataset + "intersect_kodiak_summer.npy")
    assert np.array_equal(supply_intersection[1], array2), "array2 intersections do not match"


def test_intersection_col(supply_intersection):
    col = 9600
    assert supply_intersection[2] == col, "columns do not match"


def test_intersection_row(supply_intersection):
    row = 8114
    assert supply_intersection[3] == row, "rows do not match"


def test_intersection_bounds(supply_intersection):
    bounds = (402000.0, 690000.0, 6222780.0, 6466200.0)
    assert supply_intersection[4] == bounds, "Bounding box does not match"


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
