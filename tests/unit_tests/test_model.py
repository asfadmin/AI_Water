import os

from hypothesis import given
from src.config import PROJECT_DIR
from src.model import path_from_model_name
from tests.strategies import model_component


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


@given(model_component(), model_component())
def test_fuzz_path_from_model_name(network_name, tag):
    assert path_from_model_name(f"{network_name}:{tag}") == os.path.join(
        PROJECT_DIR, "models", network_name, f"{tag}.h5"
    )
