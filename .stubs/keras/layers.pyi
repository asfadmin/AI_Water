from typing import Tuple


class Layer(object):
    ...


class Input(Layer):
    def __init__(self, shape: Tuple[int, ...]) -> None:
        ...
