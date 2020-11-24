"""
    Contains the architecture for creating a cropland data layer within SAR images.
"""

from keras.layers import Activation, BatchNormalization, Dropout, Input, Layer, TimeDistributed
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.merge import concatenate
from keras.layers.pooling import MaxPooling2D
from keras.models import Model
from keras.optimizers import Adam
from src.config import NETWORK_DEMS as dems


def conv2d_block_time_dist(
    input_tensor: Input,
    num_filters: int,
    kernel_size: int = 3,
    batchnorm: bool = True
) -> Layer:
    """ Function to add 2 convolutional layers with the parameters
    passed to it """
    # first layer
    x = TimeDistributed(
        Conv2D(
            filters=num_filters,
            kernel_size=(kernel_size, kernel_size),
            kernel_initializer='he_normal',
            padding='same'
        )
    )(input_tensor)
    if batchnorm:
        x = TimeDistributed(BatchNormalization())(x)
    x = TimeDistributed(Activation('relu'))(x)
    # second layer
    x = TimeDistributed(
        Conv2D(
            filters=num_filters,
            kernel_size=(kernel_size, kernel_size),
            kernel_initializer='he_normal',
            padding='same'
        )
    )(input_tensor)
    if batchnorm:
        x = TimeDistributed(BatchNormalization())(x)
    x = TimeDistributed(Activation('relu'))(x)

    return x


""" Cropland Data Time Series version of U-net model used in masked.py """


def create_cdl_model_masked(
    model_name: str,
    num_filters: int = 16,
    time_steps: int = 5,
    dropout: float = 0.1,
    batchnorm: bool = True
) -> Model:
    """ Function to define the Time Distributed UNET Model """

    """Requires stack of Sequential SAR data (with vh vv channels stacked), where each image is a different timestep"""
    inputs = Input(shape=(time_steps, dems, dems, 2))

    c1 = conv2d_block_time_dist(
        inputs, num_filters * 1, kernel_size=3, batchnorm=batchnorm
    )
    p1 = TimeDistributed(MaxPooling2D((2, 2)))(c1)
    p1 = TimeDistributed(Dropout(dropout))(p1)

    c2 = conv2d_block_time_dist(p1, num_filters * 2, kernel_size=3, batchnorm=batchnorm)
    p2 = TimeDistributed(MaxPooling2D((2, 2)))(c2)
    p2 = TimeDistributed(Dropout(dropout))(p2)

    c3 = conv2d_block_time_dist(p2, num_filters * 4, kernel_size=3, batchnorm=batchnorm)
    p3 =TimeDistributed( MaxPooling2D((2, 2)))(c3)
    p3 = TimeDistributed(Dropout(dropout))(p3)

    c4 = conv2d_block_time_dist(p3, num_filters * 8, kernel_size=3, batchnorm=batchnorm)
    p4 = TimeDistributed(MaxPooling2D((2, 2)))(c4)
    p4 = Dropout(dropout)(p4)

    c5 = conv2d_block_time_dist(p4, num_filters * 8, kernel_size=3, batchnorm=batchnorm)
    p5 = TimeDistributed(MaxPooling2D((2, 2)))(c5)
    p5 = TimeDistributed(Dropout(dropout))(p5)

    c6 = conv2d_block_time_dist(
        p5, num_filters * 8, kernel_size=3, batchnorm=batchnorm
    )
    p6 = TimeDistributed(MaxPooling2D((2, 2)))(c6)
    p6 = TimeDistributed(Dropout(dropout))(p6)

    c7 = conv2d_block_time_dist(
        p6, num_filters=num_filters * 16, kernel_size=3, batchnorm=batchnorm
    )

    # Expanding to 64 x 64 x 1
    u8 = TimeDistributed(Conv2DTranspose(
        num_filters * 4, (3, 3), strides=(2, 2), padding='same'
    ))(c7)
    u8 = concatenate([u8, c6])
    u8 = TimeDistributed(Dropout(dropout))(u8)
    c8 = conv2d_block_time_dist(u8, num_filters * 4, kernel_size=3, batchnorm=batchnorm)

    u9 = TimeDistributed(Conv2DTranspose(
        num_filters * 2, (3, 3), strides=(2, 2), padding='same'
    ))(c8)
    u9 = concatenate([u9, c5])
    u9 = TimeDistributed(Dropout(dropout))(u9)
    c9 = conv2d_block_time_dist(u9, num_filters * 2, kernel_size=3, batchnorm=batchnorm)

    u10 = TimeDistributed(Conv2DTranspose(
        num_filters * 1, (3, 3), strides=(2, 2), padding='same'
    ))(c9)

    u10 = concatenate([u10, c4])
    u10 = TimeDistributed(Dropout(dropout))(u10)
    c10 = conv2d_block_time_dist(
        u10, num_filters * 1, kernel_size=3, batchnorm=batchnorm
    )

    u11 = TimeDistributed(Conv2DTranspose(
        num_filters * 1, (3, 3), strides=(2, 2), padding='same'
    ))(c10)

    u11 = concatenate([u11, c3])
    u11 = TimeDistributed(Dropout(dropout))(u11)
    c11 = conv2d_block_time_dist(
        u11, num_filters * 1, kernel_size=3, batchnorm=batchnorm
    )

    u12 = TimeDistributed(Conv2DTranspose(
        num_filters * 1, (3, 3), strides=(2, 2), padding='same'
    ))(c11)
    u12 = concatenate([u12, c2])
    u12 = TimeDistributed(Dropout(dropout))(u12)
    c12 = conv2d_block_time_dist(
        u12, num_filters * 1, kernel_size=3, batchnorm=batchnorm
    )

    u13 = TimeDistributed(Conv2DTranspose(
        num_filters * 1, (3, 3), strides=(2, 2), padding='same'
    ))(c12)
    u13 = concatenate([u13, c1])
    u13 = TimeDistributed(Dropout(dropout))(u13)
    c13 = conv2d_block_time_dist(
        u13, num_filters * 1, kernel_size=3, batchnorm=batchnorm
    )

    outputs = TimeDistributed(Conv2D(1, (1, 1), activation='sigmoid', name='last_layer'))(c13)
    model = Model(inputs=inputs, outputs=[outputs])

    model.__asf_model_name = model_name

    model.compile(
        loss='mean_squared_error', optimizer=Adam(), metrics=['accuracy']
    )

    return model
