"""
 Created By:   Jason Herning
 Date Created: 12-16-2020
 File Name:    test_metadata_class.py
 Description:  unit test for Product class
"""

from src.metadata_class import Product, get_cmr_granule_shape
from datetime import datetime
from shapely.geometry import Polygon

tp1 = Product(name='S1A_IW_20200624T224520_DVP_RTC10_G_gpuned_8437.zip',
              granule='S1A_IW_GRDH_1SDV_20200624T224520_20200624T224545_033165_03D795_F52E',
              url='https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_20200624T224520_DVP_RTC10_G_gpuned_8437.zip')

tp1_expected_json = '{"name": "S1A_IW_20200624T224520_DVP_RTC10_G_gpuned_8437.zip", "granule": "S1A_IW_GRDH_1SDV_20200624T224520_20200624T224545_033165_03D795_F52E", "url": "https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_20200624T224520_DVP_RTC10_G_gpuned_8437.zip", "shape": "None", "start": "2020-06-24T22:45:20", "end": "2020-06-24T22:45:45"}'
tp1_expected_shape = Polygon([(106.958633, 10.517628), (107.266937, 12.030143), (105.000557, 12.471607), (104.704994, 10.962944), (106.958633, 10.517628)])


def test_product_datetime():
    expected_start = datetime(2020, 6, 24, 22, 45, 20)
    expected_end = datetime(2020, 6, 24, 22, 45, 45)

    assert tp1.start == expected_start
    assert tp1.end == expected_end

#
def test_product_to_json():
    assert tp1.to_json() == tp1_expected_json


def test_product_cmr_shape():
    cmr_shape = get_cmr_granule_shape(tp1.granule)
    assert tp1_expected_shape == cmr_shape


