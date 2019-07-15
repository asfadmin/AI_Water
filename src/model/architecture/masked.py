"""
    Contains the architecture for creating a water mask within SAR images.
"""

from keras import Tensor
from keras.layers import Activation, BatchNormalization, Dropout, Input
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.merge import concatenate
from keras.layers.pooling import MaxPooling2D
from keras.models import Model
from keras.optimizers import Adam


def conv2d_block(
    input_tensor: Tensor,
    n_filters: int,
    kernel_size: int = 3,
    batchnorm: bool = True
):
    """Function to add 2 convolutional layers with the parameters
    passed to it"""
    # first layer
    x = Conv2D(
        filters=n_filters,
        kernel_size=(kernel_size, kernel_size),
        kernel_initializer='he_normal',
        padding='same'
    )(input_tensor)
    if batchnorm:
        x = BatchNormalization()(x)
    x = Activation('relu')(x)
    # second layer
    x = Conv2D(
        filters=n_filters,
        kernel_size=(kernel_size, kernel_size),
        kernel_initializer='he_normal',
        padding='same'
    )(input_tensor)
    if batchnorm:
        x = BatchNormalization()(x)
    x = Activation('relu')(x)

    return x


def create_model_masked(
    model_name: str,
    n_filters: int = 16,
    dropout: float = 0.1,
    batchnorm: bool = True
):
    """ Function to define the UNET Model """

    inputs = Input(shape=(512, 512, 1))

    c1 = conv2d_block(inputs, n_filters * 1, kernel_size=3, batchnorm=batchnorm)
    p1 = MaxPooling2D((2, 2))(c1)
    p1 = Dropout(dropout)(p1)

    c2 = conv2d_block(p1, n_filters * 2, kernel_size=3, batchnorm=batchnorm)
    p2 = MaxPooling2D((2, 2))(c2)
    p2 = Dropout(dropout)(p2)

    c3 = conv2d_block(p2, n_filters * 4, kernel_size=3, batchnorm=batchnorm)
    p3 = MaxPooling2D((2, 2))(c3)
    p3 = Dropout(dropout)(p3)

    c4 = conv2d_block(p3, n_filters * 8, kernel_size=3, batchnorm=batchnorm)
    p4 = MaxPooling2D((2, 2))(c4)
    p4 = Dropout(dropout)(p4)

    c4_5 = conv2d_block(p4, n_filters * 8, kernel_size=3, batchnorm=batchnorm)
    p4_5 = MaxPooling2D((2, 2))(c4_5)
    p4_5 = Dropout(dropout)(p4_5)

    c4_6 = conv2d_block(p4_5, n_filters * 8, kernel_size=3, batchnorm=batchnorm)
    p4_6 = MaxPooling2D((2, 2))(c4_6)
    p4_6 = Dropout(dropout)(p4_6)

    c5 = conv2d_block(
        p4_6, n_filters=n_filters * 16, kernel_size=3, batchnorm=batchnorm
    )
    # Expansive Path
    u7 = Conv2DTranspose(n_filters * 4, (3, 3), strides=(2, 2),
                         padding='same')(c5)
    u7 = concatenate([u7, c4_6])
    u7 = Dropout(dropout)(u7)
    c7 = conv2d_block(u7, n_filters * 4, kernel_size=3, batchnorm=batchnorm)

    u8 = Conv2DTranspose(n_filters * 2, (3, 3), strides=(2, 2),
                         padding='same')(c7)
    u8 = concatenate([u8, c4_5])
    u8 = Dropout(dropout)(u8)
    c8 = conv2d_block(u8, n_filters * 2, kernel_size=3, batchnorm=batchnorm)

    u9 = Conv2DTranspose(n_filters * 1, (3, 3), strides=(2, 2),
                         padding='same')(c8)
    u9 = concatenate([u9, c4])
    u9 = Dropout(dropout)(u9)
    c9 = conv2d_block(u9, n_filters * 1, kernel_size=3, batchnorm=batchnorm)

    u10 = Conv2DTranspose(
        n_filters * 1, (3, 3), strides=(2, 2), padding='same'
    )(c9)
    u10 = concatenate([u10, c3])
    u10 = Dropout(dropout)(u10)
    c10 = conv2d_block(u10, n_filters * 1, kernel_size=3, batchnorm=batchnorm)

    u11 = Conv2DTranspose(
        n_filters * 1, (3, 3), strides=(2, 2), padding='same'
    )(c10)
    u11 = concatenate([u11, c2])
    u11 = Dropout(dropout)(u11)
    c11 = conv2d_block(u11, n_filters * 1, kernel_size=3, batchnorm=batchnorm)

    u12 = Conv2DTranspose(
        n_filters * 1, (3, 3), strides=(2, 2), padding='same'
    )(c11)
    u12 = concatenate([u12, c1])
    u12 = Dropout(dropout)(u12)
    c12 = conv2d_block(u12, n_filters * 1, kernel_size=3, batchnorm=batchnorm)

    outputs = Conv2D(1, (1, 1), activation='sigmoid', name='last_layer')(c12)
    model = Model(inputs=inputs, outputs=[outputs])

    model.__asf_model_name = model_name

    model.compile(
        loss='mean_squared_error', optimizer=Adam(), metrics=['accuracy']
    )

    return model
