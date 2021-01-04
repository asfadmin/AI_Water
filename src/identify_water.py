import argparse
import pathlib
from contextlib import contextmanager
from typing import Any, Callable, Iterator, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RectangleSelector, Slider, PolygonSelector
from matplotlib.path import Path
from osgeo import gdal
import time


@contextmanager
def gdal_open(file_name: Union[str, pathlib.Path]) -> Iterator[gdal.Dataset]:
    file_name = str(file_name)
    f = gdal.Open(file_name)
    if not f:
        raise FileNotFoundError(file_name)
    yield f

class Product:
    def __init__(self, vv_image_path: str, vh_image_path: str):
        self.load_images(vv_image_path, vh_image_path)
        self.clip_images()
        self.mask_number = 0
    
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

def show_images(prod) -> None:
    plt.figure()
    images = ((prod.vv_image, 'VV'), (prod.vh_image, 'VH'))
    for i, (img, title) in enumerate(images):
        plt.subplot(1, len(images), i + 1)
        plt.title(title)
        plt.imshow(img, cmap=plt.cm.gist_gray)

# Creates a grid of coordinates that is pruned to be as small is it can while
# still containing the whole polygon from the polyselector.
def prune(prod, verts):
    ind_start = time.perf_counter()

    # Find the min/max y value of the vertices.
    min_y = verts[0][1]
    max_y = verts[0][1]
    min_x = verts[0][0]
    max_x = verts[0][0]
    for v in verts:
        if v[1] < min_y:
            min_y = v[1]
        if v[1] > max_y:
            max_y = v[1]
        if v[0] < min_x:
            min_x = v[0]
        if v[0] > max_x:
            max_x = v[0]

    # Coordinate Grid that ends up as indices for editing the mask
    g = np.meshgrid(
        np.arange(0, len(prod.vv_image[0][:]))[int(min_x):int(max_x)],
        np.arange(0, len(prod.vv_image[:][0]))[int(min_y):int(max_y)]
    )
    coords = list(zip(*(c.flat for c in g)))

    ind_end = time.perf_counter()
    print("Create Indices Time: ", ind_end - ind_start)
    prune_start = time.perf_counter()

    offset = len(prod.vv_image[:][0])
    coords_pruned = coords[0:]
    
    prune_end = time.perf_counter()
    print("Pruning Time: ", prune_end - prune_start)
    
    return coords_pruned

def show_mask(prod, mask: np.ndarray) -> None:

    filter = (
        abs(prod.vh_image.mean() - (prod.vh_image.std() 
        if prod.vh_image.mean() > 0.005 
        else prod.vh_image.min()))
    )
    min = 0.0
    max = (
        prod.vh_image.mean() if prod.vv_image.mean() < prod.vh_image.mean() 
        else prod.vh_image.mean()
    )

    # Update function for the PolygonSelector
    def onselect(verts):
        print("Creating Indices")
        
        # Path based on the verticies from the selection
        path = Path(verts)

        coords_pruned = prune(prod, verts)

        path_start = time.perf_counter()

        # Array of indices that are within the polygon 
        ind = np.vstack(
            [
                [p[0] for p in coords_pruned if path.contains_point(p)],
                [p[1] for p in coords_pruned if path.contains_point(p)]
            ]
        )

        path_end = time.perf_counter()
        print("Point in Polygon Time: ", path_end - path_start)

        mask_start = time.perf_counter()
        mask_edited = edit_mask_from_selection(mask, 1, verts, ind)
        mask_end = time.perf_counter()
        print("Mask Editing Time: ", mask_end - mask_start)
        return show_mask(prod, mask_edited)

    def update(val):
        show_mask(prod, create_mask(prod.vv_image, prod.vh_image, val))

    mat = plt.matshow(mask)
    ax = plt.gca()

    # Calls onselect with an array of tuples defining the verticies of the polygon
    # Note: this is called any time the plot is clicked on!
    selector = PolygonSelector(plt.gca(), onselect)

    filter_slider = Slider(plt.axes([0.5, 0.025, 0.25, 0.04])
                           , 'Filter'
                           , min
                           , (max-min)/ 2
                           , valinit=filter
                           , valstep=max/10000
                    )
    filter_slider.on_changed(update)

    button = Button(plt.axes([0.1, 0.025, 0.1, 0.04]), 'Save GeoTiff')
    button.on_clicked(
        lambda _: write_mask_to_file(
            mask, f'mask-{prod.mask_number}.tif', prod.projection, prod.geo_transform
        )
    )

    x = prod.vv_array
    y = prod.vh_array

    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

    axs[0].hist(x, bins=50)
    axs[1].hist(y, bins=50)

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
    vv_image: np.ndarray, vh_image: np.ndarray, filter: float
) -> np.ndarray:

    mask = np.zeros(vv_image.shape)
    indices = ()

    vvmin = vv_image.min()
    vhmin = vh_image.min()
    vvmean = vv_image.mean()
    vhmean = vh_image.mean()
    vvstd = vv_image.std()
    vhstd = vh_image.std()

    if vv_image.mean() < vh_image.mean():
        indices = np.where(
            np.logical_and(
                 vv_image <= filter,
                np.logical_and(vv_image != 0, vh_image != 0)
            )
        )

    else:
        indices = np.where(
            np.logical_and(
                vh_image <= filter,
                np.logical_and(vv_image != 0, vh_image != 0)
            )
        )

    mask[indices] = 1

    return mask

def edit_mask_from_selection(
   mask: np.ndarray, filter: float, selection: tuple, indices
) -> np.ndarray:

    print("Creating Edited Mask")

    indices[[0, 1]] = indices[[1, 0]]
    mask[tuple(indices)] = 0

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
