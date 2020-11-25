"""
 Created By:   Jason Herning
 Date Started: 08-07-2020
 File Name:    test_config.py
 Description:  unit test for compressing datasets
"""

import os

import pytest
from src.io_tools import remove_subdirectories, compress_datasets, get_sar_paths, make_directory_dataset, \
    list_sar_directory
from pathlib import Path
from src.asf_typing import sar_set
import random


@pytest.fixture(scope="function")
def supply_datadir_cwd(datadir, monkeypatch):
    """Fixture to patch current working directory to datadir."""
    monkeypatch.chdir(datadir)
    test_make_data_path = Path(f'../test_compress_dataset').resolve()
    monkeypatch.chdir(test_make_data_path)


def tree(directory):
    """print directory tree of given Path object"""
    print(f'+ {directory}')
    for path in sorted(directory.rglob('*')):
        depth = len(path.relative_to(directory).parts)
        spacer = '    ' * depth
        print(f'{spacer}+ {path.name}')


directory_anchorage_test = ["test_1.mask.tif",
                            "test_1.vh.tif",
                            "test_1.vv.tif",
                            "test_2.mask.tif",
                            "test_2.vh.tif",
                            "test_2.vv.tif"]

directory_alaska = ["test_1.mask.tif",
                    "test_1.vh.tif",
                    "test_1.vv.tif",
                    "test_2.mask.tif",
                    "test_2.vh.tif",
                    "test_2.vv.tif",
                    "test_3.mask.tif",
                    "test_3.vh.tif",
                    "test_3.vv.tif",
                    "test_4.mask.tif",
                    "test_4.vh.tif",
                    "test_4.vv.tif",
                    "test_5.mask.tif",
                    "test_5.vh.tif",
                    "test_5.vv.tif",
                    "test_6.mask.tif",
                    "test_6.vh.tif",
                    "test_6.vv.tif",
                    "test_7.mask.tif",
                    "test_7.vh.tif",
                    "test_7.vv.tif",
                    "test_8.mask.tif",
                    "test_8.vh.tif",
                    "test_8.vv.tif"]


# Tests for list_sar_directory
@pytest.mark.usefixtures("supply_datadir_cwd")
@pytest.mark.parametrize("input_path, expected_list", [('datasets/Alaska', directory_alaska),
                                                       ('datasets/Alaska/Anchorage/test', directory_anchorage_test)])
def test_list_sar_directory_match(input_path, expected_list):
    """Test that that the output list matches the expected."""
    input_files = list_sar_directory(input_path)
    assert input_files == expected_list, f"input_files {input_files} does NOT match {expected_list}"


sar_set_anchorage_test = [sar_set(Path('datasets/Alaska/Anchorage/test/test_1.mask.tif'),
                                  Path('datasets/Alaska/Anchorage/test/test_1.vh.tif'),
                                  Path('datasets/Alaska/Anchorage/test/test_1.vv.tif')),
                          sar_set(Path('datasets/Alaska/Anchorage/test/test_2.mask.tif'),
                                  Path('datasets/Alaska/Anchorage/test/test_2.vh.tif'),
                                  Path('datasets/Alaska/Anchorage/test/test_2.vv.tif'))]

sar_set_alaska_test = [sar_set(Path('datasets/Alaska/Anchorage/test/test_1.mask.tif'),
                               Path('datasets/Alaska/Anchorage/test/test_1.vh.tif'),
                               Path('datasets/Alaska/Anchorage/test/test_1.vv.tif')),
                       sar_set(Path('datasets/Alaska/Anchorage/test/test_2.mask.tif'),
                               Path('datasets/Alaska/Anchorage/test/test_2.vh.tif'),
                               Path('datasets/Alaska/Anchorage/test/test_2.vv.tif')),
                       sar_set(Path('datasets/Alaska/Anchorage/train/test_3.mask.tif'),
                               Path('datasets/Alaska/Anchorage/train/test_3.vh.tif'),
                               Path('datasets/Alaska/Anchorage/train/test_3.vv.tif')),
                       sar_set(Path('datasets/Alaska/Anchorage/train/test_4.mask.tif'),
                               Path('datasets/Alaska/Anchorage/train/test_4.vh.tif'),
                               Path('datasets/Alaska/Anchorage/train/test_4.vv.tif')),
                       sar_set(Path('datasets/Alaska/Fairbanks/test/test_5.mask.tif'),
                               Path('datasets/Alaska/Fairbanks/test/test_5.vh.tif'),
                               Path('datasets/Alaska/Fairbanks/test/test_5.vv.tif')),
                       sar_set(Path('datasets/Alaska/Fairbanks/test/test_6.mask.tif'),
                               Path('datasets/Alaska/Fairbanks/test/test_6.vh.tif'),
                               Path('datasets/Alaska/Fairbanks/test/test_6.vv.tif')),
                       sar_set(Path('datasets/Alaska/Fairbanks/train/test_7.mask.tif'),
                               Path('datasets/Alaska/Fairbanks/train/test_7.vh.tif'),
                               Path('datasets/Alaska/Fairbanks/train/test_7.vv.tif')),
                       sar_set(Path('datasets/Alaska/Fairbanks/train/test_8.mask.tif'),
                               Path('datasets/Alaska/Fairbanks/train/test_8.vh.tif'),
                               Path('datasets/Alaska/Fairbanks/train/test_8.vv.tif'))]


# Tests for get_sars_paths()
@pytest.mark.usefixtures("supply_datadir_cwd")
@pytest.mark.parametrize("input_path, expected_list", [('datasets/Alaska/Anchorage/test', sar_set_anchorage_test),
                                                       ('datasets/Alaska', sar_set_alaska_test)])
def test_get_sars_paths_match(input_path, expected_list):
    """Test that the list of sar_sets(mask,vh,vv) matches the given Path input"""
    input_files = get_sar_paths(input_path)
    assert input_files == expected_list, f"input_files {input_files} does NOT match {expected_list}"


# Tests for remove_subdirectories()
@pytest.mark.usefixtures("supply_datadir_cwd")
@pytest.mark.parametrize("input_path, expected_list", [('datasets/Alaska', [])])
def test_remove_subdirectories_list(input_path, expected_list):
    """Test that the remaining subdirectory list matches"""
    remove_subdirectories(input_path)
    input_list = os.listdir(input_path)
    assert input_list == expected_list, f"listdir(): {input_list} does NOT match {expected_list}"


@pytest.mark.usefixtures("supply_datadir_cwd")
@pytest.mark.parametrize("input_path, expected_list", [('datasets/Alaska', {'train', 'test'})])
def test_remove_subdirectories_test_train(input_path, expected_list):
    """Test that the test and train folder remain after script is ran"""
    make_directory_dataset(input_path)
    remove_subdirectories(input_path)
    input_list = set(os.listdir(input_path))
    assert input_list == expected_list, f"listdir(): {input_list} does NOT match {expected_list}"


# Tests for compress_datasets()
@pytest.mark.usefixtures("supply_datadir_cwd")
@pytest.mark.parametrize("input_path, expected_sars, expected_random_calls", [('datasets/Alaska', 24, 8),
                                                                              ('datasets/Alaska/Anchorage/test', 6, 2)])
def test_compress_datasets(input_path, expected_sars, expected_random_calls, mocker):
    total_sars = len(list_sar_directory(input_path))

    spy_random = mocker.spy(random, 'random')

    compress_datasets(input_path, holdout=.2)

    assert spy_random.call_count == expected_random_calls, f"got {spy_random} random calls, expected {expected_random_calls}. "
    assert os.listdir(input_path) == ['train', 'test'], f"tree: {tree(Path(input_path))}"
    assert total_sars == expected_sars, f"rglob: {list_sar_directory(input_path)}"

