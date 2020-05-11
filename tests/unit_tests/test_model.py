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
    ModelType, load_history, load_model, model_type, path_from_model_name,
    save_history, save_model
)
from src.model.architecture.masked import create_model_masked as create_model
from src.asf_typing import History
from tests.strategies import model_component
from src.config import NETWORK_DEMS as dems

@pytest.fixture
def model_name(tmpdir: py.path.local):
    model = "unittest_model"
    temp_model_dir = tmpdir.mkdir("models")
    shutil.copytree(
        "tests/data/models/sample_model", temp_model_dir.join(model)
    )
    with mock.patch("src.model.MODELS_DIR", temp_model_dir):
        yield model


@pytest.fixture
def fake_model() -> Model:
    model = Sequential([
        Flatten(input_shape=(512, 512, 2)),
        Dense(1, activation='sigmoid')
    ])
    model.compile('adam', loss='binary_crossentropy')
    return model


@pytest.fixture
def fake_model_masked() -> Model:
    return Sequential([Dense(1, input_shape=(dems, dems, 2))])


@pytest.fixture
def fake_model_other() -> Model:
    return Sequential([Dense(1, input_shape=(512, 512, 512, 2))])


@pytest.fixture
def new_history() -> History:
    return {
        "accuracy": [.25, .27, .30],
        "loss": [1.3, 1.1, 1.0],
        "val_accuracy": [.26, .29, .28],
        "val_loss": [1.4, 0.8, 0.9]
    }


def test_create_model():
    # Verifying that create_model doesn't throw any errors
    model_masked = create_model("some_masked_model")
    assert model_masked.__asf_model_name == "some_masked_model"


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


def test_load_model(model_name: str, fake_model: Model):
    with mock.patch('src.model.kload_model', return_value=fake_model):
        model = load_model(model_name)

    assert model.__asf_model_name == model_name
    assert model.__asf_model_history


def verify_model_layer_equality(m1: Model, m2: Model):
    for l1, l2 in zip(m1.layers, m2.layers):
        assert l1.input_shape == l2.input_shape
        assert l1.output_shape == l2.output_shape


def test_save_model(model_name: str, fake_model: Model):
    fake_model.__asf_model_name = f"{model_name}:some_old_tag"

    save_model(fake_model, "test_save_model")
    model = load_model(f"{model_name}:test_save_model")

    verify_model_layer_equality(model, fake_model)


def test_save_model_with_history(
    model_name: str, fake_model: Model, new_history: History
):
    fake_model.__asf_model_name = f"{model_name}:some_old_tag"

    save_model(fake_model, "test_save_model", history=new_history)
    model = load_model(f"{model_name}:test_save_model")

    verify_model_layer_equality(model, fake_model)
    assert model.__asf_model_history == new_history


def test_save_model_no_dir(
    model_name: str, tmpdir: py.path.local, fake_model: Model
):
    shutil.rmtree(tmpdir.join("models"))

    fake_model.__asf_model_name = f"{model_name}:some_old_tag"
    save_model(fake_model, "test_save_model")

    assert tmpdir.join("models").check(dir=1)


def test_load_history(model_name: str):
    history = load_history(model_name)

    for key in ('accuracy', 'loss', 'val_accuracy', 'val_loss'):
        assert key in history


def test_save_history(model_name: str, new_history: History):
    save_history(new_history, model_name)

    history = load_history(model_name)
    assert history == new_history


def test_save_history_no_dir(
    model_name: str, tmpdir: py.path.local, new_history: History
):
    shutil.rmtree(tmpdir.join("models"))

    save_history(new_history, model_name)

    assert tmpdir.join("models").check(dir=1)


def test_model_type(
    fake_model: Model, fake_model_masked: Model, fake_model_other: Model
):

    assert model_type(fake_model_masked) == ModelType.MASKED
    assert model_type(fake_model_other) is None
