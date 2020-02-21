"""
 Jason Herning
 2-14-2020
 test_mask_subscription.py
 Test functions for mask_subscription.py
"""


import pytest
import re
from datetime import datetime
from math import floor
from scripts.mask_subscription import product_middle_time, triage_products




def test_triage_products():

    assert triage_products(product_list_unsorted_1) == product_list_sorted_1, "unsorted and sorted list do not match."




def test_product_middle_time():

    file = "S1A_IW_GRDH_1SDV_20190903T023810_20190903T023830_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip"
    
    middle_time = datetime(2019, 9, 3, 2, 38, 20)

    assert product_middle_time(file) == middle_time





# sub_id 1872
product_list_unsorted_1 = [{'id': 119993, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023801_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023801_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 812891707, 'creation_date': '2019-09-04 02:24:31.093008+00:00', 'group_ids': []},
                           {'id': 119995, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190903T151616_20190903T151641_017875_021A3E_DBB5-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190903T151616_20190903T151641_017875_021A3E_DBB5-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151616_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151616_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 354669390, 'creation_date': '2019-09-04 02:35:47.224627+00:00', 'group_ids': []},
                           {'id': 120002, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190903T151551_20190903T151616_017875_021A3E_325A-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190903T151551_20190903T151616_017875_021A3E_325A-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151551_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151551_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 692144996, 'creation_date': '2019-09-04 04:27:55.804444+00:00', 'group_ids': []},
                           {'id': 120004, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T023736_20190903T023801_028851_0344EE_AA7E-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T023736_20190903T023801_028851_0344EE_AA7E-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023736_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023736_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 749360343, 'creation_date': '2019-09-04 04:47:18.802347+00:00', 'group_ids': []},
                           {'id': 120005, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T024056_20190903T024121_028851_0344EE_D6D4-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T024056_20190903T024121_028851_0344EE_D6D4-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024056_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024056_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 769290977, 'creation_date': '2019-09-04 05:04:49.917224+00:00', 'group_ids': []},
                           {'id': 120006, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T024031_20190903T024056_028851_0344EE_FD7B-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T024031_20190903T024056_028851_0344EE_FD7B-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024031_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024031_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 777871509, 'creation_date': '2019-09-04 05:21:28.368435+00:00', 'group_ids': []},
                           {'id': 120007, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T024121_20190903T024144_028851_0344EE_3D0E-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T024121_20190903T024144_028851_0344EE_3D0E-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024121_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024121_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 423017364, 'creation_date': '2019-09-04 05:34:21.471518+00:00', 'group_ids': []},
                           {'id': 120009, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190903T151526_20190903T151551_017875_021A3E_0D04-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190903T151526_20190903T151551_017875_021A3E_0D04-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151526_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151526_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 803550844, 'creation_date': '2019-09-04 05:50:32.429778+00:00', 'group_ids': []},
                           {'id': 120012, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T023711_20190903T023736_028851_0344EE_741D-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T023711_20190903T023736_028851_0344EE_741D-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023711_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023711_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 585591387, 'creation_date': '2019-09-04 06:05:54.708278+00:00', 'group_ids': []},
                           {'id': 120036, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190904T022817_20190904T022842_017882_021A6E_8864-PREDORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190904T022817_20190904T022842_017882_021A6E_8864-PREDORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022817_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022817_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 758544089, 'creation_date': '2019-09-04 08:30:05.285228+00:00', 'group_ids': []},
                           {'id': 120037, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190904T022842_20190904T022910_017882_021A6E_9CCA-PREDORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190904T022842_20190904T022910_017882_021A6E_9CCA-PREDORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022842_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022842_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 880250710, 'creation_date': '2019-09-04 08:31:25.208042+00:00', 'group_ids': []}]


product_list_sorted_1 = [{'id': 120012, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T023711_20190903T023736_028851_0344EE_741D-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T023711_20190903T023736_028851_0344EE_741D-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023711_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023711_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 585591387, 'creation_date': '2019-09-04 06:05:54.708278+00:00', 'group_ids': []},
                         {'id': 120004, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T023736_20190903T023801_028851_0344EE_AA7E-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T023736_20190903T023801_028851_0344EE_AA7E-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023736_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023736_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 749360343, 'creation_date': '2019-09-04 04:47:18.802347+00:00', 'group_ids': []},
                         {'id': 119993, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023801_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T023801_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 812891707, 'creation_date': '2019-09-04 02:24:31.093008+00:00', 'group_ids': []},
                         {'id': 120006, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T024031_20190903T024056_028851_0344EE_FD7B-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T024031_20190903T024056_028851_0344EE_FD7B-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024031_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024031_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 777871509, 'creation_date': '2019-09-04 05:21:28.368435+00:00', 'group_ids': []},
                         {'id': 120005, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T024056_20190903T024121_028851_0344EE_D6D4-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T024056_20190903T024121_028851_0344EE_D6D4-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024056_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024056_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 769290977, 'creation_date': '2019-09-04 05:04:49.917224+00:00', 'group_ids': []},
                         {'id': 120007, 'sub_id': 1872, 'name': 'S1A_IW_GRDH_1SDV_20190903T024121_20190903T024144_028851_0344EE_3D0E-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20190903T024121_20190903T024144_028851_0344EE_3D0E-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024121_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1A_IW_RT30_20190903T024121_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 423017364, 'creation_date': '2019-09-04 05:34:21.471518+00:00', 'group_ids': []},
                         {'id': 120009, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190903T151526_20190903T151551_017875_021A3E_0D04-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190903T151526_20190903T151551_017875_021A3E_0D04-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151526_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151526_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 803550844, 'creation_date': '2019-09-04 05:50:32.429778+00:00', 'group_ids': []},
                         {'id': 120002, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190903T151551_20190903T151616_017875_021A3E_325A-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190903T151551_20190903T151616_017875_021A3E_325A-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151551_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151551_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 692144996, 'creation_date': '2019-09-04 04:27:55.804444+00:00', 'group_ids': []},
                         {'id': 119995, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190903T151616_20190903T151641_017875_021A3E_DBB5-RESORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190903T151616_20190903T151641_017875_021A3E_DBB5-RESORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151616_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190903T151616_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 354669390, 'creation_date': '2019-09-04 02:35:47.224627+00:00', 'group_ids': []},
                         {'id': 120036, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190904T022817_20190904T022842_017882_021A6E_8864-PREDORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190904T022817_20190904T022842_017882_021A6E_8864-PREDORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022817_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022817_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 758544089, 'creation_date': '2019-09-04 08:30:05.285228+00:00', 'group_ids': []},
                         {'id': 120037, 'sub_id': 1872, 'name': 'S1B_IW_GRDH_1SDV_20190904T022842_20190904T022910_017882_021A6E_9CCA-PREDORB-30m-amp-rtc-gamma.zip', 'url': 'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20190904T022842_20190904T022910_017882_021A6E_9CCA-PREDORB-30m-amp-rtc-gamma.zip', 'browse_url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022842_G_gan_rgb.png', 'browse_thumbnail': {'url': 'https://hyp3-download.asf.alaska.edu/asf/browse/S1B_IW_RT30_20190904T022842_G_gan_rgb.thumb.png', 'epsg': None, 'resolution': None, 'lat_min': None, 'lat_max': None, 'lon_min': None, 'lon_max': None}, 'browse_geo_images': [], 'browse_geo_xml': None, 'process_id': 2, 'size': 880250710, 'creation_date': '2019-09-04 08:31:25.208042+00:00', 'group_ids': []}]



# for p in product_list_unsorted_1:
    # print(p["name"])
    # print(f"""start time: {product_middle_time(p['name'])[0]}""")
    # print(f"""time elapsed: {product_middle_time(p['name'])[1] - product_middle_time(p['name'])[0]} \n""")

    # print(f"""{product_middle_time(p['name'])[0]} ==> {product_middle_time(p['name'])[1]}________{product_middle_time(p['name'])[1] - product_middle_time(p['name'])[0]}""")


# product_list_sorted_1 = sorted(product_list_unsorted_1, key=lambda product: product_middle_time(product['name']))



# print("==========================")
# for p in product_list_sorted_1:
#     # print(p["name"])
#     print(f"""start time: {product_middle_time(p['name'])}""")


# print(product_list_sorted_1)