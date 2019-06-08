import os
import shutil
from typing import Set

import mock
import numpy as np
import pytest
from hypothesis import given
from src.dataset import (
    generate_from_metadata, load_labels, make_label_conversions, make_metadata
)
from src.typing import DatasetMetadata
from tests.strategies import classes


@pytest.fixture
def sample_dataset(tempdir: str):
    dataset = "unittest_dataset"
    os.mkdir(os.path.join(tempdir, "dataset"))
    temp_dataset_dir = os.path.join(tempdir, "dataset")
    shutil.copytree(
        "tests/data/sample_dataset", os.path.join(temp_dataset_dir, dataset)
    )
    with mock.patch("src.dataset.DATASET_DIR", temp_dataset_dir):
        yield dataset


@pytest.fixture
def metadata() -> DatasetMetadata:
    return [("test_file_1", "water"), ("test_file_2", "not_water")]


def test_load_labels(sample_dataset: str):
    labels = load_labels(sample_dataset)

    assert labels["test_file_1"] == "water"
    assert labels["test_file_2"] == "not_water"
    assert labels["test_file_3"] == "invalid"
    assert labels["test_file_4"] == "skip"


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


def filter_pathname(metadata: DatasetMetadata) -> DatasetMetadata:
    return list(map(lambda x: (os.path.basename(x[0]), x[1]), metadata))


def test_make_metadata(sample_dataset: str):
    train_metadata, test_metadata = make_metadata(sample_dataset)

    # Normally these are returned with absolute paths, but for verification we
    # just need the file names.
    train_metadata = filter_pathname(train_metadata)
    test_metadata = filter_pathname(test_metadata)

    assert train_metadata == [
        ("test_file_2", "not_water"),
        ("test_file_4", "skip"),
    ]
    assert test_metadata == [
        ("test_file_1", "water"),
        ("test_file_3", "invalid"),
    ]


def filter_classes(
    metadata: DatasetMetadata, classes: Set[str]
) -> DatasetMetadata:
    return list(filter(lambda x: x[1] in classes, metadata))


@given(classes())
def test_make_metadata_with_classes(sample_dataset: str, classes: Set[str]):
    train_metadata, test_metadata = make_metadata(
        sample_dataset, classes=classes
    )

    train_metadata = filter_pathname(train_metadata)
    test_metadata = filter_pathname(test_metadata)

    assert train_metadata == filter_classes([
        ("test_file_2", "not_water"),
        ("test_file_4", "skip"),
    ], classes)
    assert test_metadata == filter_classes([
        ("test_file_1", "water"),
        ("test_file_3", "invalid"),
    ], classes)


def generate_data(metadata: DatasetMetadata, img: np.ndarray):
    mock_Open = mock.Mock()
    mock_Open.return_value.ReadAsArray.return_value = img

    with mock.patch("src.dataset.gdal.Open", mock_Open):
        generator = generate_from_metadata(
            metadata, label_to_num={
                "water": 1,
                "not_water": 0
            }
        )

        return list(generator)


def test_generate_from_metadata(metadata: DatasetMetadata):
    data = generate_data(metadata, np.zeros((512, 512)) + 1)

    imgs = list(map(lambda x: x[0], data))
    labels = list(map(lambda x: x[1], data))
    for img in imgs:
        assert (img == np.zeros((512, 512, 1)) + 1).all()

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
