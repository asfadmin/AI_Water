import argparse
import pathlib
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RectangleSelector, Slider
from osgeo import gdal


@contextmanager
def gdal_open(file_name: Union[str, pathlib.Path]) -> Iterator[gdal.Dataset]:
    file_name = str(file_name)
    f = gdal.Open(file_name)
    if not f:
        raise FileNotFoundError(file_name)
    yield f


class Application(object):
    def __init__(self, bins: int, verbose: int):
        self.bins = bins
        self.verbose = verbose

    def run(self, vv_image_path: str, vh_image_path: str) -> None:
        if self.verbose:
            print("Reading files")

        self.load_images(vv_image_path, vh_image_path)
        self.clip_images()

        if self.verbose:
            print("Plotting")

        self.show_images()
        self.interactive_histogram()

    def load_images(self, vv_image_path: str, vh_image_path: str) -> None:
        with gdal_open(vv_image_path) as f:
            self.vv_image = f.ReadAsArray()
            vv_projection = f.GetProjection()
            vv_geo_transform = f.GetGeoTransform()

        with gdal_open(vh_image_path) as f:
            self.vh_image = f.ReadAsArray()
            vh_projection = f.GetProjection()
            vh_geo_transform = f.GetGeoTransform()

        assert vv_projection == vh_projection, 'Images must have matching projections'
        assert vv_geo_transform == vh_geo_transform, 'Images must have matching geo transforms'

        self.projection = vv_projection
        self.geo_transform = vv_geo_transform

    def clip_images(self) -> None:
        self.vv_array = self.vv_image.flatten()
        self.vh_array = self.vh_image.flatten()

        vv_mean = self.vv_array.mean()
        vv_stdev = self.vv_array.std()
        vh_mean = self.vh_array.mean()
        vh_stdev = self.vh_array.std()

        self.vv_image.clip(0, vv_mean + 2 * vv_stdev, out=self.vv_image)
        self.vh_image.clip(0, vh_mean + 2 * vh_stdev, out=self.vh_image)

        self.vv_array = self.vv_image.flatten()
        self.vh_array = self.vh_image.flatten()

    def show_images(self) -> None:
        plt.figure()
        images = ((self.vv_image, 'VV'), (self.vh_image, 'VH'))
        for i, (img, title) in enumerate(images):
            plt.subplot(1, len(images), i + 1)
            plt.title(title)
            plt.imshow(img, cmap=plt.cm.gist_gray)

    def interactive_histogram(self) -> None:
        # Filter out no data values
        self.vv_array = self.vv_array[self.vv_array != 0]
        self.vh_array = self.vh_array[self.vh_array != 0]

        self.selected = ()

        fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.25, bottom=0.25)

        sbin = Slider(
            plt.axes([0.25, 0.15, 0.65, 0.03]),
            'Bins',
            1,
            200,
            valstep=1,
            valinit=self.bins
        )
        sbin.on_changed(
            lambda val: plt.
            hist2d(self.vv_array, self.vh_array, bins=val, cmap=plt.cm.jet)
        )

        button = Button(
            plt.axes([0.8, 0.025, 0.1, 0.04]), 'Mask', hovercolor='0.975'
        )

        self.mask_number = 0

        def mask_clicked(event) -> None:
            if not self.selected:
                return

            (vv_min, vh_min), (vv_max, vh_max) = self.selected
            mask = create_mask(
                self.vv_image, self.vh_image, vv_min, vv_max, vh_min, vh_max
            )
            self.show_mask(mask)
            self.mask_number += 1

        button.on_clicked(mask_clicked)
        _close_button = close_button()

        hist_ax = plt.axes()
        plt.xlabel('VV')
        plt.ylabel('VH')
        plt.hist2d(
            self.vv_array, self.vh_array, bins=self.bins, cmap=plt.cm.jet
        )

        def line_select_callback(eclick, erelease) -> None:
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata

            self.selected = ((x1, y1), (x2, y2))

        rs = RectangleSelector(
            hist_ax,
            line_select_callback,
            drawtype='box',
            useblit=False,
            button=[1],
            minspanx=5,
            minspany=5,
            spancoords='pixels',
            interactive=True
        )
        plt.colorbar()
        plt.show()

    def show_mask(self, mask: np.ndarray) -> None:
        plt.figure()
        plt.imshow(mask)
        button = Button(plt.axes([0.8, 0.025, 0.1, 0.04]), 'Save GeoTiff')
        button.on_clicked(
            lambda _: write_mask_to_file(
                mask, f'mask-{self.mask_number}.tif', self.projection, self.
                geo_transform
            )
        )
        plt.show()


def close_button(callback: Optional[Callable[[Any], None]] = None) -> object:
    """ Create a 'close' button on the plot. Make sure to save this to a value.
    """
    button = Button(plt.axes([0.05, 0.05, 0.1, 0.075]), 'Close')

    def click_handler(event: Any) -> None:
        if callback:
            callback(event)
        plt.close('all')

    button.on_clicked(click_handler)
    # Need to return the button to prevent it from being garbage collected
    return button


def create_mask(
    vv_image: np.ndarray, vh_image: np.ndarray, vv_min: float, vv_max: float,
    vh_min: float, vh_max: float
) -> np.ndarray:
    mask = np.zeros(vv_image.shape)
    indecies = np.where(
        np.logical_and(
            np.logical_and(vv_image >= vv_min, vv_image < vv_max),
            np.logical_and(vh_image >= vh_min, vh_image < vh_max)
        )
    )
    mask[indecies] = 1

    return mask


def write_mask_to_file(
    mask: np.ndarray, file_name: str, projection: str, geo_transform: str
) -> None:
    (width, height) = mask.shape
    out_image = gdal.GetDriverByName('GTiff').Create(
        file_name, height, width, bands=1
    )
    out_image.SetProjection(projection)
    out_image.SetGeoTransform(geo_transform)
    out_image.GetRasterBand(1).WriteArray(mask)
    out_image.FlushCache()


def main(vv_image_path: str, vh_image_path: str) -> None:
    app = Application(bins=75, verbose=1)
    app.run(vv_image_path, vh_image_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('vv_image_path', help='Path to the VV file')
    parser.add_argument('vh_image_path', help='Path to the VH file')

    args = parser.parse_args()
    main(args.vv_image_path, args.vh_image_path)
