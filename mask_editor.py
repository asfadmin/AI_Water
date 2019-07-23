#! /usr/bin/env python3

import argparse
import pathlib
from contextlib import contextmanager
from typing import Iterator, Union

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import RectangleSelector
from osgeo import gdal

# Key bindings
KEY_FILL_0 = '0'
KEY_FILL_1 = '1'
KEY_UNDO = 'u'
KEY_SAVE = 'w'


@contextmanager
def gdal_open(file_name: Union[str, pathlib.Path]) -> Iterator[gdal.Dataset]:
    file_name = str(file_name)
    f = gdal.Open(file_name)
    if not f:
        raise FileNotFoundError(file_name)
    yield f


def write_mask_to_file(
    f: gdal.Dataset, file_name: str, mask: np.ndarray
) -> None:
    (width, height) = mask.shape
    out_image = gdal.GetDriverByName('GTiff').Create(
        file_name, height, width, bands=1
    )
    out_image.SetProjection(f.GetProjection())
    out_image.SetGeoTransform(f.GetGeoTransform())
    out_image.GetRasterBand(1).WriteArray(mask)
    out_image.FlushCache()


def interactive_editor(mask_path: str) -> None:
    with gdal_open(mask_path) as f:
        mask = f.ReadAsArray()
        f = f

    selection = ()
    previous_values = None
    previous_selection = ()

    fig, ax = plt.subplots()
    im = plt.imshow(mask)
    plt.text(
        0,
        1.1, (
            f"Press '{KEY_FILL_0}' to fill zeros, "
            f"'{KEY_FILL_1}' to fill ones, "
            f"'{KEY_UNDO}' to undo the last fill and "
            f"'{KEY_SAVE}' to save the mask "
        ),
        transform=ax.transAxes
    )
    saved_text = plt.text(0.5, 1, "saved", transform=ax.transAxes)

    def selector_handler(eclick, erelease) -> None:
        nonlocal selection
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        selection = (x1, y1, x2, y2)

    def key_pressed(event) -> None:
        nonlocal previous_values
        nonlocal previous_selection
        if not selection:
            return

        # Keys that don't care about the selection data
        if event.key == KEY_SAVE:
            write_mask_to_file(f, mask_path, mask)
            saved_text.set_visible(True)
            fig.canvas.draw()
            return
        elif event.key == KEY_UNDO:
            if previous_values is not None:
                x1, y1, x2, y2 = previous_selection
                mask[y1:y2, x1:x2] = previous_values
                im.set_data(mask)
                fig.canvas.draw()
            return

        saved_text.set_visible(False)
        x1, y1, x2, y2 = list(map(int, selection))
        previous_values = np.array(mask[y1:y2, x1:x2])
        previous_selection = (x1, y1, x2, y2)

        if event.key == KEY_FILL_0:
            mask[y1:y2, x1:x2] = 0
        elif event.key == KEY_FILL_1:
            mask[y1:y2, x1:x2] = 1

        im.set_data(mask)
        fig.canvas.draw()

    selector = RectangleSelector(
        ax, selector_handler, drawtype='box', interactive=True
    )
    plt.connect('key_press_event', key_pressed)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mask_file', help='Path to the mask GeoTiff')

    args = parser.parse_args()
    interactive_editor(args.mask_file)
