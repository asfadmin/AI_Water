import json
import os
import re
from enum import Enum
from typing import Optional, Tuple

from keras import backend
from keras.layers import (
    Activation, BatchNormalization, Conv2D, Input, MaxPooling2D, UpSampling2D,
    concatenate
)
from keras.losses import binary_crossentropy
from keras.models import Model
from keras.models import load_model as kload_model
from keras.optimizers import Adam

from .config import MODELS_DIR
from .typing import History


class ModelType(Enum):
    BINARY = 0
    MASKED = 1


def down(filters, input):
    down = Conv2D(filters, (3, 3), padding='same')(input)
    down = BatchNormalization(epsilon=1e-4)(down)
    down = Activation('relu')(down)
    down = Conv2D(filters, (3, 3), padding='same')(down)
    down = BatchNormalization(epsilon=1e-4)(down)
    down_res = Activation('relu')(down)
    down_pool = MaxPooling2D((2, 2), strides=(2, 2))(down)
    return down_pool, down_res


def up(filters, input, down):
    up = UpSampling2D((2, 2))(input)
    up = concatenate([down, up], axis=3)
    up = Conv2D(filters, (3, 3), padding='same')(up)
    up = BatchNormalization(epsilon=1e-4)(up)
    up = Activation('relu')(up)
    up = Conv2D(filters, (3, 3), padding='same')(up)
    up = BatchNormalization(epsilon=1e-4)(up)
    up = Activation('relu')(up)
    up = Conv2D(filters, (3, 3), padding='same')(up)
    up = BatchNormalization(epsilon=1e-4)(up)
    up = Activation('relu')(up)
    return up


def create_model(model_name: str) -> Model:
    num_classes = 1
    inputs = Input(shape=(512, 512, 1))

    down_0a, down_0a_res = down(24, inputs)
    down_0, down_0_res = down(64, down_0a)
    down_1, down_1_res = down(128, down_0)
    down_2, down_2_res = down(256, down_1)
    down_3, down_3_res = down(512, down_2)
    down_4, down_4_res = down(768, down_3)

    center = Conv2D(768, (3, 3), padding='same')(down_4)
    center = BatchNormalization(epsilon=1e-4)(center)
    center = Activation('relu')(center)
    center = Conv2D(768, (3, 3), padding='same')(center)
    center = BatchNormalization(epsilon=1e-4)(center)
    center = Activation('relu')(center)

    up_4 = up(768, center, down_4_res)
    up_3 = up(512, up_4, down_3_res)
    up_2 = up(256, up_3, down_2_res)
    up_1 = up(128, up_2, down_1_res)
    up_0 = up(64, up_1, down_0_res)
    up_0a = up(24, up_0, down_0a_res)

    classify = Conv2D(num_classes, (1, 1), activation='sigmoid', name='last_layer')(up_0a)

    model = Model(inputs=inputs, outputs=classify)

    model.__asf_model_name = model_name
    
    model.compile(loss=dice_loss, optimizer=Adam(), metrics=['accuracy'])
    return model


def coef(y_true, y_pred, smooth=1):
    y_true_f = backend.flatten(y_true)
    y_pred_f = backend.flatten(y_pred)

    intersection = backend.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (backend.sum(y_true_f) + backend.sum(y_pred_f) + smooth)


def dice_coef_loss(y_true, y_pred):
    return 1-coef(y_true, y_pred)


def dice_loss(y_true, y_pred):
    return binary_crossentropy(y_true, y_pred) + coef_loss(y_true, y_pred)


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
    name, _ = name_tag_from_model_name(model.__asf_model_name)
    model_path = path_from_model_name_tag(name, model_tag)
    model_dir = os.path.dirname(model_path)

    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)

    if history:
        save_history_to_path(history, model_dir)

    model.save(model_path)


def load_model(model_name: str) -> Model:
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
        json.dump(history, f)


def load_history(model_name: str) -> History:
    model_path = path_from_model_name(model_name)
    model_dir = os.path.dirname(model_path)

    return load_history_from_path(model_dir)


def load_history_from_path(model_dir: str) -> History:
    with open(os.path.join(model_dir, "history.json")) as f:
        return json.load(f)


def model_type(model: Model) -> Optional[ModelType]:
    if model.output_shape == (None, 1):
        return ModelType.BINARY
    if model.output_shape == (None, 512, 512, 1):
        return ModelType.MASKED

    return None
