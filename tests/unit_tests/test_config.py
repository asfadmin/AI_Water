"""
 Created By:   Jason Herning
 Date Started: 07-08-2020
 File Name:    test_config.py
 Description:  unit test for config.py
"""

import re
import pytest
from src.config import VV_REGEX, VH_REGEX, ZIP_REGEX


# tests for VV_REGEX()
@pytest.mark.parametrize("input_string, expected_bool", [("s1b_iw_rt30_20190624t224459_g_gpn_83.vv.tif", True),
                                                         ("s1b_iw_rt30_20190624t224459_g_gpn_83.vh.tif", False),
                                                         (".tif", False),
                                                         ("abc", False),
                                                         ("s_12345_.tif", False)])
def test_VV_REGEX(input_string, expected_bool):
    input = bool(re.search(VV_REGEX, input_string))
    expected = expected_bool
    assert input == expected, f"regex {input} does NOT match {expected}"


# tests for VH_REGEX()
@pytest.mark.parametrize("input_string, expected_bool", [("s1b_iw_rt30_20190624t224459_g_gpn_83.vh.tif", True),
                                                         ("s1b_iw_rt30_20190624t224459_g_gpn_83.vv.tif", False),
                                                         (".tif", False),
                                                         ("abc", False),
                                                         ("s_12345_.tif", False)])
def test_VH_REGEX(input_string, expected_bool):
    input = bool(re.search(VH_REGEX, input_string))
    expected = expected_bool
    assert input == expected, f"regex {input} does NOT match {expected}"


# tests for ZIP_REGEX()
@pytest.mark.parametrize("input_string, expected_bool", [
    ("S1A_IW_GRDH_1SDV_20190919T001902_20190919T001927_029083_034D00_5E45-PREDORB-30m-amp-filt-rtc-gamma.zip", True),
    ("S1A_IW_GRDH_1SDV_20200622T211736_20200622T211801_033135_03D6B2_C54A-RESORB_30m_nomatch_power_gamma0-rtc-gamma.zip", True),
    (".tif", False),
    ("abc", False),
    ("s_12345_.tif", False)])
def test_ZIP_REGEX(input_string, expected_bool):
    input = bool(re.search(ZIP_REGEX, input_string))
    expected = expected_bool
    assert input == expected, f"regex {input} does NOT match {expected}"
