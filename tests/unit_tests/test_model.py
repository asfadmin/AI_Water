import os
import shutil

import mock
import py
import pytest
from hypothesis import given
from keras.layers import Dense, Flatten
from keras.models import Model, Sequential
from src.config import PROJECT_DIR
from src.model import (
    create_model, load_history, load_model, path_from_model_name, save_history,
    save_model
)
from src.typing import History
from tests.strategies import model_component


@pytest.fixture
def sample_model(tmpdir: py.path.local):
    model = "unittest_model"
    temp_model_dir = tmpdir.mkdir("models")
    shutil.copytree(
        "tests/data/models/sample_model", temp_model_dir.join(model)
    )
    with mock.patch("src.model.MODELS_DIR", temp_model_dir):
        yield model


@pytest.fixture
def fake_model() -> Model:
    return Sequential([
        Flatten(input_shape=(512, 512)),
        Dense(1, activation='sigmoid')
    ])


@pytest.fixture
def new_history() -> History:
    return {
        "acc": [.25, .27, .30],
        "loss": [1.3, 1.1, 1.0],
        "val_acc": [.26, .29, .28],
        "val_loss": [1.4, 0.8, 0.9]
    }


def test_create_model():
    # Verifying that create_model doesn't throw any errors
    model = create_model("some_model")

    assert model.__asf_model_name == "some_model"


def test_path_from_model_name():
    assert path_from_model_name("example_net") == os.path.join(
        PROJECT_DIR, "models", "example_net", "latest.h5"
    )
    assert path_from_model_name("example_net:latest") == os.path.join(
        PROJECT_DIR, "models", "example_net", "latest.h5"
    )
    assert path_from_model_name("example_net:epoch1") == os.path.join(
        PROJECT_DIR, "models", "example_net", "epoch1.h5"
    )
    with pytest.raises(ValueError):
        path_from_model_name("A\nB")


@given(model_component(), model_component())
def test_fuzz_path_from_model_name(network_name, tag):
    assert path_from_model_name(f"{network_name}:{tag}") == os.path.join(
        PROJECT_DIR, "models", network_name, f"{tag}.h5"
    )


def test_load_model(sample_model: str, fake_model: Model):
    with mock.patch('src.model.kload_model', return_value=fake_model):
        model = load_model(sample_model)

    assert model.__asf_model_name == sample_model
    assert model.__asf_model_history


def verify_model_layer_equality(m1: Model, m2: Model):
    for l1, l2 in zip(m1.layers, m2.layers):
        assert l1.input_shape == l2.input_shape
        assert l1.output_shape == l2.output_shape


def test_save_model(sample_model: str, fake_model: Model):
    fake_model.__asf_model_name = f"{sample_model}:some_old_tag"

    save_model(fake_model, "test_save_model")
    model = load_model(f"{sample_model}:test_save_model")

    verify_model_layer_equality(model, fake_model)


def test_save_model_with_history(
    sample_model: str, fake_model: Model, new_history: History
):
    fake_model.__asf_model_name = f"{sample_model}:some_old_tag"

    save_model(fake_model, "test_save_model", history=new_history)
    model = load_model(f"{sample_model}:test_save_model")

    verify_model_layer_equality(model, fake_model)
    assert model.__asf_model_history == new_history


def test_save_model_no_dir(
    sample_model: str, tmpdir: py.path.local, fake_model: Model
):
    shutil.rmtree(tmpdir.join("models"))

    fake_model.__asf_model_name = f"{sample_model}:some_old_tag"
    save_model(fake_model, "test_save_model")

    assert tmpdir.join("models").check(dir=1)


def test_load_history(sample_model: str):
    history = load_history(sample_model)

    for key in ('acc', 'loss', 'val_acc', 'val_loss'):
        assert key in history


def test_save_history(sample_model: str, new_history: History):
    save_history(new_history, sample_model)

    history = load_history(sample_model)
    assert history == new_history


def test_save_history_no_dir(
    sample_model: str, tmpdir: py.path.local, new_history: History
):
    shutil.rmtree(tmpdir.join("models"))

    save_history(new_history, sample_model)

    assert tmpdir.join("models").check(dir=1)
