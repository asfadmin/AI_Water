import itertools
import os
import shutil
from contextlib import contextmanager
from typing import Set

import mock
import numpy as np
import py
import pytest
from hypothesis import given
from src.dataset import (
    generate_from_metadata, load_dataset, load_labels, make_label_conversions,
    make_metadata
)
from src.typing import DatasetMetadata
from tests.strategies import classes


@pytest.fixture
def sample_dataset(tmpdir: py.path.local):
    dataset = "unittest_dataset"
    temp_dataset_dir = tmpdir.mkdir("datasets")

    shutil.copytree("tests/data/sample_dataset", temp_dataset_dir.join(dataset))
    with mock.patch("src.dataset.binary.DATASETS_DIR", temp_dataset_dir):
        yield dataset


@pytest.fixture
def metadata() -> DatasetMetadata:
    return [("test_file_1", "water"), ("test_file_2", "not_water")]


@contextmanager
def mock_gdal_open(img: np.ndarray) -> mock.Mock:
    mock_Open = mock.Mock()
    mock_Open.return_value.ReadAsArray.return_value = img

    with mock.patch("src.dataset.gdal.Open", mock_Open):
        yield mock_Open


def test_load_labels(sample_dataset: str):
    labels = load_labels(sample_dataset)

    assert labels["test_file_1"] == "water"
    assert labels["test_file_2"] == "not_water"
    assert labels["test_file_3"] == "invalid"
    assert labels["test_file_4"] == "skip"


def test_load_labels_corrupted(sample_dataset: str):
    with pytest.raises(ValueError):
        with mock.patch('json.load', return_value=[]):
            load_labels(sample_dataset)


def test_make_label_conversions(sample_dataset: str):
    label_to_num, num_to_label = make_label_conversions(
        sample_dataset, {"water", "not_water"}
    )

    assert label_to_num == {"water": 1, "not_water": 0}
    assert num_to_label == {1: "water", 0: "not_water"}


@given(classes())
def test_fuzz_label_conversions(sample_dataset: str, classes: Set[str]):
    label_to_num, num_to_label = make_label_conversions(
        sample_dataset, classes=classes
    )

    for k, v in label_to_num.items():
        assert num_to_label[v] == k


def test_make_metadata(sample_dataset: str, tmpdir: py.path.local):
    train_metadata, test_metadata = make_metadata(sample_dataset)

    def abspath(*f: str) -> str:
        return tmpdir.join("datasets", sample_dataset, *f)

    assert train_metadata == [
        (abspath("train", "test_file_2"), "not_water"),
        (abspath("train", "test_file_4"), "skip"),
    ]
    assert test_metadata == [
        (abspath("test", "test_file_1"), "water"),
        (abspath("test", "test_file_3"), "invalid"),
    ]


def filter_classes(
    metadata: DatasetMetadata, classes: Set[str]
) -> DatasetMetadata:
    return list(filter(lambda x: x[1] in classes, metadata))


@given(classes())
def test_make_metadata_with_classes(
    sample_dataset: str, tmpdir: py.path.local, classes: Set[str]
):
    train_metadata, test_metadata = make_metadata(
        sample_dataset, classes=classes
    )

    def abspath(*f: str) -> str:
        return tmpdir.join("datasets", sample_dataset, *f)

    assert train_metadata == filter_classes([
        (abspath("train", "test_file_2"), "not_water"),
        (abspath("train", "test_file_4"), "skip"),
    ], classes)
    assert test_metadata == filter_classes([
        (abspath("test", "test_file_1"), "water"),
        (abspath("test", "test_file_3"), "invalid"),
    ], classes)


def generate_data(metadata: DatasetMetadata, img: np.ndarray):
    with mock_gdal_open(img):
        generator = generate_from_metadata(
            metadata, label_to_num={
                "water": 1,
                "not_water": 0
            }
        )

        return list(generator)


def test_generate_from_metadata(metadata: DatasetMetadata):
    data = generate_data(metadata, np.ones((512, 512)))

    imgs = list(map(lambda x: x[0], data))
    labels = list(map(lambda x: x[1], data))
    for img in imgs:
        assert (img == np.ones((512, 512, 1))).all()

    assert labels == [1, 0]


def test_generate_from_metadata_with_zeros(
    sample_dataset: str, metadata: DatasetMetadata
):
    data = generate_data(metadata, np.zeros((512, 512)))

    assert data == []


def test_generate_from_metadata_with_nans(
    sample_dataset: str, metadata: DatasetMetadata
):
    data = generate_data(metadata, np.zeros((512, 512)) + np.nan)

    assert data == []


def test_load_dataset(sample_dataset: str):
    with mock_gdal_open(np.ones((512, 512))):
        train_iter, test_iter = load_dataset(sample_dataset)

    train = list(itertools.islice(train_iter, len(train_iter)))
    test = list(itertools.islice(test_iter, len(test_iter)))

    assert len(train) == 1
    assert len(test) == 1


def test_load_dataset_and_metadata(sample_dataset: str):
    with mock_gdal_open(np.ones((512, 512))):
        train_iter, test_iter, train_meta, test_meta = load_dataset(
            sample_dataset, get_metadata=True
        )

    train = list(itertools.islice(train_iter, len(train_iter)))
    test = list(itertools.islice(test_iter, len(test_iter)))

    assert len(train) == len(train_meta)
    assert len(test) == len(test_meta)
