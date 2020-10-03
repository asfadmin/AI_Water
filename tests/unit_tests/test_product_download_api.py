"""
 Created By:   Jason Herning
 Date Created: 08-27-2020
 File Name:    test_product_download_api.py
 Description:  unit test for functions from product_download_api.py
"""

import pytest
from src.product_download_api import metalink_to_list, download_product, MetalinkProduct, metalink_product_generator, get_netrc_credentials, credentials, download_metalink_products
from pathlib import Path
import responses
from unittest.mock import mock_open, patch, MagicMock
import functools


# TODO: Move to conftest.py because DRY.
# @pytest.fixture(scope="function")
# def supply_datadir_cwd(datadir, monkeypatch):
#     """Fixture to patch current working directory to datadir."""
#     current_file_name = Path(__file__).stem
#     monkeypatch.chdir(datadir)
#     test_cwd = Path(f'../{current_file_name}').resolve()
#     monkeypatch.chdir(test_cwd)

@pytest.fixture(scope="function")
def supply_datadir_cwd(datadir, monkeypatch):
    """Fixture to patch current working directory to datadir."""
    monkeypatch.chdir(datadir)
    test_make_data_path = Path(f'../test_product_download_api').resolve()
    monkeypatch.chdir(test_make_data_path)


# Expected list from metadata
metalink_list_1 = [
    'https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20200531T224609_20200531T224628_032815_03CD12_DF4F-RESORB-30m-power-rtc-gamma.zip',
    'https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20200525T224442_20200525T224507_021744_02944E_73B3-RESORB-30m-power-rtc-gamma.zip']


# Tests for metalink_to_list
@pytest.mark.usefixtures("supply_datadir_cwd")
@pytest.mark.parametrize("input_path, expected_list", [("products.metalink", metalink_list_1)])
def test_metalink_to_list(input_path, expected_list):
    test_list = metalink_to_list(input_path)

    assert test_list == expected_list, f"The generated test_list:{test_list}, does NOT equal expected_list:{expected_list}"


test_product_1 = MetalinkProduct(
    name="S1A_IW_GRDH_1SDV_20200531T224609_20200531T224628_032815_03CD12_DF4F-RESORB-30m-power-rtc-gamma.zip",
    url="https://hyp3-download.asf.alaska.edu/asf/data/S1A_IW_GRDH_1SDV_20200531T224609_20200531T224628_032815_03CD12_DF4F-RESORB-30m-power-rtc-gamma.zip",
    hash="438d531d9f04a01a0d3b46acae86515ae34b65f8f491f68af2423eea55e3af834e4ed6b8246a630bc164f7cda1cc7b40f40ce25313fa209d9010940a6fd928e3",
    size=328590573
)

test_product_2 = MetalinkProduct(
    name="S1B_IW_GRDH_1SDV_20200525T224442_20200525T224507_021744_02944E_73B3-RESORB-30m-power-rtc-gamma.zip",
    url="https://hyp3-download.asf.alaska.edu/asf/data/S1B_IW_GRDH_1SDV_20200525T224442_20200525T224507_021744_02944E_73B3-RESORB-30m-power-rtc-gamma.zip",
    hash="5cd84cd5789e3eb4fde1b0dae79821cdbf3721e609ebab7c26c607911e9c459fa4da680e026b8bad6bb233293c0d4114da5f8f80ccc16032775121f4e8b9e986",
    size=459077309
)


# tests for metalink_product_generator
@pytest.mark.usefixtures("supply_datadir_cwd")
def test_metalink_product_generator():
    test_generator = metalink_product_generator(Path("products.metalink"))
    input_product_1 = next(test_generator)
    input_product_2 = next(test_generator)

    assert input_product_1 == input_product_1, f"test_product:{test_product_1} != expected_product:{input_product_1}"
    assert input_product_2 == input_product_2, f"test_product:{test_product_2} != expected_product:{input_product_2}"


# Tests for get_netrc_credentials
@pytest.mark.usefixtures("supply_datadir_cwd")
def test_get_netrc_credentials():
    test_creds = get_netrc_credentials()
    expected_creds = credentials('dummy_user', 'dummy_password')
    assert test_creds == expected_creds, f"test:{test_creds} != expected:{expected_creds}"


@pytest.fixture()
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for given tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


def calltracker(func):
    @functools.wraps(func)
    def wrapper(*args):
        wrapper.has_been_called = True
        return func(*args)

    wrapper.has_been_called = False
    return wrapper


# Tests for download_product
@pytest.mark.usefixtures("supply_datadir_cwd")
# @pytest.mark.usefixtures("no_requests")
@responses.activate
def test_download_product():
    open_mock = mock_open()

    save_directory = Path.cwd()
    expected_name = save_directory / test_product_1.name

    with patch("builtins.open", open_mock):

        responses.add(responses.GET, url=test_product_1.url, status=401)
        responses.add(responses.GET, status=200)

        download_product(test_product_1.url, save_directory)

    open_mock.assert_called_with(expected_name, "wb")



# Tests for download_metalink_products
# TODO: Make test better.
@pytest.mark.usefixtures("supply_datadir_cwd")
def test_download_metalink_products():
    input_matalink_path = Path.cwd() / "products.metalink"
    save_directory_path = Path.cwd()

    download_mock = MagicMock()
    with patch("src.product_download_api.download_product", download_mock):
        download_metalink_products(input_matalink_path, save_directory_path)

    download_mock.assert_called()













