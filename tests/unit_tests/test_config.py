"""
 Created By:   Jason Herning
 Date Started: 07-08-2020
 File Name:    test_config.py
 Description:  unit test for config.py
"""

import numpy as np
import re
import pytest

from src.config import VV_REGEX, VH_REGEX


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
