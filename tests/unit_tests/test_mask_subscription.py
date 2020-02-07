
import pytest
import re



PRODUCT_REGEX = re.compile(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})_(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})')


def test_regex():


    p1 = "S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip"
    g1 = ('2019', '09', '03', '02', '38', '01', '2019', '09', '03', '02', '38', '26')

    m1 = re.search(PRODUCT_REGEX, p1)
    assert m1.groups() == g1, "test failed, groups do not match"





p1 = "S1A_IW_GRDH_1SDV_20190903T023801_20190903T023826_028851_0344EE_3AF9-RESORB-30m-amp-rtc-gamma.zip"

m = re.search(PRODUCT_REGEX, p1)

print(m)
print(m.groups())





