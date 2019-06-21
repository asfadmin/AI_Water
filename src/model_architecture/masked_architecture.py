"""
masked.py contains the architecture for creating a
water mask within SAR imgaes.
"""


from keras.layers import (
    Activation, BatchNormalization, Conv2D, Input, MaxPooling2D, UpSampling2D,
    concatenate
)
from keras.models import Model
from keras.optimizers import Adam


# input_ type is <class 'tensorflow.python.framework.ops.Tensor'>
def down(filters: int, input_):
    conv_down = Conv2D(filters, (3, 3), padding='same')(input_)
    conv_down = BatchNormalization(epsilon=1e-4)(conv_down)
    conv_down = Activation('relu')(conv_down)
    conv_down = Conv2D(filters, (3, 3), padding='same')(conv_down)
    conv_down = BatchNormalization(epsilon=1e-4)(conv_down)
    conv_down_res = Activation('relu')(conv_down)
    conv_down_pool = MaxPooling2D((2, 2), strides=(2, 2))(conv_down)
    return conv_down_pool, conv_down_res


# input_ type is <class 'tensorflow.python.framework.ops.Tensor'>
def up(filters: int, input_, down):
    conv_up = UpSampling2D((2, 2))(input_)
    conv_up = concatenate([down, conv_up], axis=3)
    conv_up = Conv2D(filters, (3, 3), padding='same')(conv_up)
    conv_up = BatchNormalization(epsilon=1e-4)(conv_up)
    conv_up = Activation('relu')(conv_up)
    conv_up = Conv2D(filters, (3, 3), padding='same')(conv_up)
    conv_up = BatchNormalization(epsilon=1e-4)(conv_up)
    conv_up = Activation('relu')(conv_up)
    conv_up = Conv2D(filters, (3, 3), padding='same')(conv_up)
    conv_up = BatchNormalization(epsilon=1e-4)(conv_up)
    conv_up = Activation('relu')(conv_up)
    return conv_up


def create_model_masked(model_name: str) -> Model:

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

    classify = Conv2D(1, (1, 1), activation='sigmoid',
                      name='last_layer')(up_0a)

    model = Model(inputs=inputs, outputs=classify)

    model.__asf_model_name = model_name

    model.compile(loss='mean_squared_error', optimizer=Adam(), metrics=['accuracy'])

    return model
