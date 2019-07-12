from typing import Any, Optional, Tuple, Union

DataType = Union[type, str]
Index = Union[int, slice, object, 'ndarray']
ArrayLike = Union['ndarray', object]


class ndarray(object):
    def __init__(
        self,
        shape: Tuple[int, ...],
        dtype: DataType = float,
        buffer: Any = None,
        offset: int = 0,
        strides: Optional[Tuple[int, ...]] = None,
        order: Optional[str] = None
    ) -> None:
        self.shape: Tuple[int, ...]
        ...

    def clip(
        self,
        min: Optional[float] = None,
        max: Optional[float] = None,
        out: Optional['ndarray'] = None
    ) -> 'ndarray':
        ...

    def flatten(self) -> 'ndarray':
        ...

    def mean(
        self,
        axis: Optional[int] = None,
        dtype: Optional[DataType] = None,
        out: Optional['ndarray'] = None
    ) -> float:
        ...

    def std(
        self,
        axis: Optional[int] = None,
        dtype: Optional[DataType] = None,
        out: Optional['ndarray'] = None,
        keepdims: bool = False
    ) -> float:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, idx: Index) -> 'ndarray':
        ...

    def __setitem__(self, idx: Index, item: Any) -> None:
        ...

    def __lt__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __le__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __eq__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __ne__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __ge__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __gt__(self, other: Any) -> 'ndarray':    # type: ignore
        ...


def logical_and(
    x1: ArrayLike,
    x2: ArrayLike,
    out: Optional[Union[ndarray, Tuple[ndarray, None]]] = None,
    *,
    where: Optional[ArrayLike] = True
) -> Union[ndarray, bool]:
    ...


def where(
    condition: Union[ndarray, bool],
    x: Optional[ArrayLike] = None,
    y: Optional[ArrayLike] = None
) -> ndarray:
    ...


def zeros(shape: Tuple[int, ...]) -> ndarray:
    ...


mean = ndarray.mean
std = ndarray.std
