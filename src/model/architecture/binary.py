"""
    Contains the architecture used to detect water within SAR images.
"""

from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Model, Sequential


def create_model_binary(model_name: str) -> Model:
    """ Creates a binary model with the output = (None, 1). """
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

    model.__asf_model_name = model_name

    return model
