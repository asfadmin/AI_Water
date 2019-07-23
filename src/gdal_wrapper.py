import pathlib
from contextlib import contextmanager
from typing import Iterator, Union

from osgeo import gdal

CPLE_TO_PYE = {
    gdal.CPLE_AppDefined: RuntimeError,
    gdal.CPLE_OutOfMemory: MemoryError,
    gdal.CPLE_FileIO: OSError,
    gdal.CPLE_OpenFailed: OSError,
    gdal.CPLE_IllegalArg: TypeError,
    gdal.CPLE_NotSupported: NotImplementedError,
    gdal.CPLE_AssertionFailed: AssertionError,
    gdal.CPLE_NoWriteAccess: PermissionError,
    gdal.CPLE_UserInterrupt: KeyboardInterrupt,
}


@contextmanager
def gdal_open(file_name: Union[str, pathlib.Path]) -> Iterator[gdal.Dataset]:
    file_name = str(file_name)
    f = gdal.Open(file_name)
    if not f:
        raise_last_error()
    yield f


def raise_last_error() -> None:
    e = gdal.GetLastErrorNo()
    if e == gdal.CPLE_None:
        return

    EClass = CPLE_TO_PYE.get(e) or RuntimeError
    ex = EClass(gdal.GetLastErrorMsg())

    if isinstance(ex, OSError):
        (msg, ) = ex.args
        if "No such file or directory" in msg:
            ex = FileNotFoundError(msg)
        elif "Permission denied" in msg:
            ex = PermissionError(msg)

        ex.strerror = msg

    raise ex
