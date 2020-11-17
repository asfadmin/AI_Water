"""
 Created By:   Jason Herning
 Date Created: 11-09-2020
 File Name:    test_io_tools.py
 Description:  unit test for functions from io_tools.py
"""

import os
import pytest
from pathlib import Path
from src.io_tools import extract_from_product

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
    output_path = input_path.parent
    vv, vh = extract_from_product(input_path, output_path)
    expected_list = ['S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VH.tif', 
                     'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VV.tif',
                     'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9.zip'
                ]
    expected_vv = output_path / 'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VV.tif'
    expected_vh = output_path / 'S1A_IW_20191203T224518_DVP_RTC10_G_gpuned_54B9_VH.tif'
    actual_list = os.listdir()
    assert expected_list == actual_list, f"EXPECTED={expected_list}, GOT={actual_list}"
    assert expected_vv == vv, f"EXPECTED={expected_vv}, GOT={vv}"
    assert expected_vh == vh, f"EXPECTED={expected_vh}, GOT={vh}"