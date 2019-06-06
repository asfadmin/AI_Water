import os
import re

from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Model, Sequential
from keras.models import load_model as kload_model

from .config import PROJECT_DIR


def create_model() -> Model:
    model = Sequential([
        Conv2D(
            64, (3, 3),
            strides=(3, 3),
            input_shape=(512, 512, 1),
            activation='relu'
        ),
        Conv2D(
            128, (3, 3),
            strides=(3, 3),
            input_shape=(512, 512, 1),
            activation='relu'
        ),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(
            128, (3, 3),
            strides=(3, 3),
            input_shape=(512, 512, 1),
            activation='relu'
        ),
        Conv2D(
            128, (3, 3),
            strides=(3, 3),
            input_shape=(512, 512, 1),
            activation='relu'
        ),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(units=128, activation='relu'),
        Dropout(rate=0.5),
        Dense(units=128, activation='relu'),
        Dropout(rate=0.5),
        Dense(units=64, activation='relu'),
        Dropout(rate=0.3),
        Dense(units=1, activation='sigmoid')
    ])

    model.compile('adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model


def path_from_model_name(model_name: str) -> str:
    """ Parse the components of a model name into a file path.

    # Example
    ```python
        assert PROJECT_DIR + "models/example_net/epoch1.h5" == \\
            path_from_model_name("example_net:epoch1")
    ```
    """
    m = re.match(r"^(.*?)(?::(.*))?$", model_name)
    if not m:
        raise ValueError("Invalid model name")

    dir_path, file_name = m.groups()
    if not file_name:
        file_name = "latest"

    return os.path.join(PROJECT_DIR, "models", dir_path, f"{file_name}.h5")


def load_model(model_name: str) -> Model:

    # with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
    pass
