"""
    Create, save, and load models and model histories. Includes helper functions
for keeping model paths consistent.
"""
import json
import os
import re
from enum import Enum
from typing import Optional, Tuple

import numpy as np
from keras.models import Model
from keras.models import load_model as kload_model

from ..config import MODELS_DIR, NETWORK_DEMS
from ..asf_typing import History


class ModelType(Enum):
    MASKED = 1


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(Encoder, self).default(obj)


def path_from_model_name(model_name: str) -> str:
    """ Parse the components of a model name into a file path.

    # Example
    ```python
        assert PROJECT_DIR + "models/example_net/epoch1.h5" == \\
            path_from_model_name("example_net:epoch1")
    ```
    """
    name, tag = name_tag_from_model_name(model_name)
    if not tag:
        tag = "latest"

    return path_from_model_name_tag(name, tag)


def name_tag_from_model_name(model_name: str) -> Tuple[str, str]:
    m = re.match(r"^(.*?)(?::(.*))?$", model_name)
    if not m:
        raise ValueError("Invalid model name")

    name, tag = m.groups()
    return name, tag or ''


def path_from_model_name_tag(name: str, tag: str) -> str:
    return os.path.join(MODELS_DIR, name, f"{tag}.h5")


def save_model(
    model: Model, model_tag: str, history: Optional[History] = None
) -> None:
    """ Creates a .h5 file (HDF5) with the architecture, weights,
    training configuration, and the state of the optimizer. """

    name, _ = name_tag_from_model_name(model.__asf_model_name)
    model_path = path_from_model_name_tag(name, model_tag)
    model_dir = os.path.dirname(model_path)

    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)

    if history:
        save_history_to_path(history, model_dir)

    model.save(model_path)


def load_model(model_name: str) -> Model:
    """ Loads and returns a model. Attaches the model name and that model's
    history. """
    model_path = path_from_model_name(model_name)
    model_dir = os.path.dirname(model_path)

    model = kload_model(model_path)
    history = load_history_from_path(model_dir)

    # Attach our extra data to the model
    model.__asf_model_name = model_name
    model.__asf_model_history = history

    return model


def save_history(history: History, model_name: str) -> None:
    model_path = path_from_model_name(model_name)
    model_dir = os.path.dirname(model_path)

    save_history_to_path(history, model_dir)


def save_history_to_path(history: History, model_dir: str) -> None:
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)

    with open(os.path.join(model_dir, "history.json"), 'w') as f:
        json.dump(history, f, cls=Encoder)


def load_history(model_name: str) -> History:
    model_path = path_from_model_name(model_name)
    model_dir = os.path.dirname(model_path)

    return load_history_from_path(model_dir)


def load_history_from_path(model_dir: str) -> History:
    with open(os.path.join(model_dir, "history.json")) as f:
        return json.load(f)


def model_type(model: Model, dem=NETWORK_DEMS) -> Optional[ModelType]:
    if model.output_shape == (None, dem, dem, 1):
        return ModelType.MASKED
