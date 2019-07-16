from typing import Any, Dict, List, Optional, Union

import numpy as np

from .layers import Input, Layer
from .optimizers import Optimizer

Generator = Any


class History(object):
    history: Dict[str, Any]


class Model(object):
    __asf_model_name: str    # Not actually part of Keras
    __asf_model_history: Dict[str, List[float]]

    def __init__(
        self, inputs: Union[Input, List[Input]],
        outputs: Union[Layer, List[Layer]]
    ) -> None:
        ...

    def compile(
        self,
        optimizer: Union[Optimizer, str],
        loss: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        loss_weights: Optional[List[float]] = None,
        sample_weight_mode: Optional[str] = None,
        weighted_metrics: Optional[List[str]] = None
    ) -> None:
        ...

    def fit_generator(
        self,
        generator: Generator,
        steps_per_epoch: int,
        epochs: int = 1,
        verbose: int = 1,
        callbacks: Optional[List[Any]] = None,
        validation_data: Optional[Generator] = None,
        validation_steps: Optional[int] = None,
        validation_freq: int = 1,
        class_weight: Optional[Dict[int, float]] = None,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
        shuffle: bool = True,
        initial_epoch: int = 0
    ) -> History:
        ...

    def predict_generator(
        self,
        generator: Generator,
        steps: Optional[int] = None,
        callbacks: Optional[List[Any]] = None,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
        verbose: int = 0
    ) -> np.ndarray:
        ...

    def summary(self) -> None:
        ...


class Sequential(Model):
    def __init__(self, layers: List[Layer]):
        ...
