from typing import Any, Callable
from typing import Iterator as TIterator
from typing import List, Optional, Tuple, Union

import numpy as np
from typing_extensions import Literal

DataFormat = Literal['channels_first', 'channels_last']
FillMode = Literal['constant', 'nearest', 'reflect', 'wrap']
SaveFormat = Literal['jpeg', 'png']
Subset = Literal['training', 'validation']


class Iterator(object):
    def __len__(self) -> int:
        ...

    def __iter__(self) -> TIterator[np.ndarray]:
        ...

    def reset(self) -> None:
        ...


class ImageDataGenerator(object):
    def __init__(
        self,
        featurewise_center: bool = False,
        samplewise_center: bool = False,
        featurewise_std_normalization: bool = False,
        samplewise_std_normalization: bool = False,
        zca_whitening: bool = False,
        zca_epsilon: float = 1e-06,
        rotation_range: int = 0,
        width_shift_range: float = 0.0,
        height_shift_range: float = 0.0,
        brightness_range: Optional[Tuple[float, float]] = None,
        shear_range: float = 0.0,
        zoom_range: float = 0.0,
        channel_shift_range: float = 0.0,
        fill_mode: FillMode = 'nearest',
        cval: float = 0.0,
        horizontal_flip: bool = False,
        vertical_flip: bool = False,
        rescale: Optional[float] = None,
        preprocessing_function: Optional[Callable[[np.ndarray], np.ndarray]
                                         ] = None,
        data_format: Optional[DataFormat] = None,
        validation_split: float = 0.0,
        dtype: Optional[Any] = None
    ) -> None:
        ...

    def flow(
        self,
        x: Union[np.ndarray, Tuple[np.ndarray, np.ndarray]],
        y: Optional[np.ndarray] = None,
        batch_size: int = 32,
        shuffle: bool = True,
        sample_weight: Optional[List[float]] = None,
        seed: Optional[int] = None,
        save_to_dir: Optional[str] = None,
        save_prefix: str = '',
        save_format: SaveFormat = 'png',
        subset: Optional[Subset] = None
    ) -> Iterator:
        ...
