"""
 Created By:   Jason Herning
 Date Created: 11-09-2020
 File Name:    test_io_tools.py
 Description:  unit test for functions from io_tools.py
"""

import os
import pytest
from pathlib import Path
from src.io_tools import extract_from_product, polygon_from_shapefile
from shapely.geometry import Polygon


@pytest.fixture(scope="function")
def supply_datadir_cwd(datadir, monkeypatch):
    """Fixture to patch current working directory to datadir."""
    monkeypatch.chdir(datadir)
    test_make_data_path = Path(f'../test_io_tools').resolve()
    monkeypatch.chdir(test_make_data_path)


@pytest.mark.usefixtures("supply_datadir_cwd")
def test_extract_from_product():
    """Test that files vv/vh tif files are extracted"""
    input_path = Path('S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9.zip')
    output_path = input_path.parent / "output"
    vv, vh = extract_from_product(input_path, output_path)
    expected_set = {'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VH.tif',
                    'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VV.tif'}
    expected_vv = output_path / 'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VV.tif'
    expected_vh = output_path / 'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VH.tif'
    actual_set = set(os.listdir("output"))
    assert expected_set == actual_set, f"EXPECTED={expected_set}, GOT={actual_set}"
    assert expected_vv == vv, f"EXPECTED={expected_vv}, GOT={vv}"
    assert expected_vh == vh, f"EXPECTED={expected_vh}, GOT={vh}"


@pytest.mark.usefixtures("supply_datadir_cwd")
def test_polygon_from_shapefile():
    input_path = Path('gnis_mekong_aoi')
    expected_polygon = Polygon(
        [(107.0317, 10.4263),
         (106.6634, 9.8288),
         (106.1069, 9.3295),
         (104.6049, 11.4617),
         (106.0455, 11.9568),
         (107.0317, 10.4263)])
    assert polygon_from_shapefile(input_path) == expected_polygon

