
import pytest
import re
from datetime import datetime



# PRODUCT_REGEX = re.compile(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})_(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})')
# PRODUCT_REGEX = re.compile(r"""S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T
#                                         (?P<start_hour>\d{2})(?P<start_minute>\d{2})(?P<start_second>\d{2})_
#                                         (?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T
#                                         (?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_[0-9]*_.*.zip""")

PRODUCT_REGEX = re.compile(r'S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T(?P<start_hour>\d{2})(?P<start_minute>\d{2})(?P<start_second>\d{2})_(?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T(?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_[0-9]*_.*.zip')

def product_datetime(product_name):
    """takes in product time; uses regex to take out the date/time of the file name
       then returns a date time object"""




def test_regex():


    p1 = "S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip"
    g1 = ('2019', '09', '03', '02', '38', '01', '2019', '09', '03', '02', '38', '26')

    m1 = re.search(PRODUCT_REGEX, p1)
    assert m1.groups() == g1, "test failed, groups do not match"





p1 = "S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip"

m = re.match(PRODUCT_REGEX, p1)



print(m.groupdict())
# print(m.groups())


# print(PRODUCT_REGEX.groups(p1))





