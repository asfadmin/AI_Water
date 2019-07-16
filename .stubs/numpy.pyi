from typing import Any, Optional, Tuple, Union

from typing_extensions import Literal

ArrayLike = Union['ndarray', object]
Casting = Literal['no', 'equiv', 'safe', 'same_kind', 'unsafe']
DataType = Union[type, str]
Index = Union[int, slice, object, 'ndarray']
Order = Literal['K', 'A', 'C', 'F']
Shape = Tuple[int, ...]


class ndarray(object):
    def __init__(
        self,
        shape: Shape,
        dtype: DataType = float,
        buffer: Any = None,
        offset: int = 0,
        strides: Optional[Shape] = None,
        order: Optional[str] = None
    ) -> None:
        self.shape: Shape
        ...

    def any(
        self: ArrayLike,
        axis: Optional[Union[int, Tuple[int, ...]]] = None,
        out: Optional['ndarray'] = None,
        keepdims: bool = False
    ) -> bool:
        ...

    def astype(
        self,
        dtype: DataType,
        order: Order = 'K',
        casting: Casting = 'unsafe',
        subok: bool = True,
        copy: bool = True
    ) -> 'ndarray':
        ...

    def clip(
        self: ArrayLike,
        min: Optional[float] = None,
        max: Optional[float] = None,
        out: Optional['ndarray'] = None
    ) -> 'ndarray':
        ...

    def flatten(self) -> 'ndarray':
        ...

    def mean(
        self: ArrayLike,
        axis: Optional[int] = None,
        dtype: Optional[DataType] = None,
        out: Optional['ndarray'] = None
    ) -> float:
        ...

    def reshape(
        self: ArrayLike, newshape: Shape, order: Order = 'C'
    ) -> 'ndarray':
        ...

    def round(
        self: ArrayLike, decimals: int = 0, out: Optional['ndarray'] = None
    ) -> 'ndarray':
        ...

    def std(
        self: ArrayLike,
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

    def __iter__(self) -> Any:
        ...

    def __contains__(self, other: Any) -> 'ndarray':
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

    def __add__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __truediv__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __iadd__(self, other: Any) -> 'ndarray':    # type: ignore
        ...

    def __itruediv__(self, other: Any) -> 'ndarray':    # type: ignore
        ...


def array(
    object: ArrayLike,
    dtype: Optional[DataType] = None,
    copy: bool = True,
    order: Order = 'K',
    subok: bool = False,
    ndmin: int = 0
) -> ndarray:
    ...


def isnan(
    x: ArrayLike,
    out: Optional[Union[ndarray, Tuple[ndarray, None]]] = None,
    *,
    where: ArrayLike = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DataType] = None,
    subok: bool = True
) -> Union[ndarray, bool]:
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


any = ndarray.any
around = ndarray.round
clip = ndarray.clip
mean = ndarray.mean
reshape = ndarray.reshape
std = ndarray.std
