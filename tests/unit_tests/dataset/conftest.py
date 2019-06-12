from contextlib import contextmanager

import mock
import numpy as np


@contextmanager
def mock_gdal_open(img: np.ndarray) -> mock.Mock:
    mock_Open = mock.Mock()
    mock_Open.return_value.ReadAsArray.return_value = img

    with mock.patch("osgeo.gdal.Open", mock_Open):
        yield mock_Open
