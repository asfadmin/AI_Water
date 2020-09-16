"""
 Created By:   Jason Herning
 Date Started: 07-31-2020
 File Name:    test_apt_funtions.py
 Description:  unit test for api_functions.py
"""


import pytest
from src.api_functions import metalink_to_list
import xml.etree.ElementTree as ET
from pathlib import Path


path_cwd = Path(__file__).parent.absolute()


# Tests for metalink_to_list
def test_metalink_to_list():

    metalink_path = path_cwd / 'testing_data' / 'products.metalink'

    test_list = metalink_to_list(str(metalink_path))
    expected_list = ['https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20200531T224609_20200531T224628_032815_03CD12_DF4F-RESORB-30m-power-rtc-gamma.zip', 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20200525T224442_20200525T224507_021744_02944E_73B3-RESORB-30m-power-rtc-gamma.zip']
    assert test_list == expected_list







# # Tests for metalink_to_list
# def test_metalink_to_list(monkeypatch):
#     def mock_parse(xml_string):
#         return ET.fromstring(xml_string)
#
#     monkeypatch.setattr(ET, 'parse', mock_parse(metalink_xml_1))
#
#     test_list = metalink_to_list(metalink_xml_1)
#     expected_list = ['https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20200531T224609_20200531T224628_032815_03CD12_DF4F-RESORB-30m-power-rtc-gamma.zip', 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20200525T224442_20200525T224507_021744_02944E_73B3-RESORB-30m-power-rtc-gamma.zip']
#     assert test_list == expected_list
