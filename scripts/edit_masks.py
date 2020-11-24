"""
 McKade Sorensen
 11-11-19
 edit_mask.py
"""
import re
from argparse import ArgumentParser
import os
from typing import Tuple

from src.plots import edit_predictions
from src.asf_cnn import test_model_masked
from src.model import load_model
from src.config import PROJECT_DIR
from osgeo import gdal
from src.config import NETWORK_DEMS as dems

def make_tiles(ifname: str,
               tile_size: Tuple[int, int],
               folder: str) -> None:
    """ Takes a .tiff file and breaks it into smaller .tiff files. """

    img_fpath = os.path.join(PROJECT_DIR, ifname, folder)

    datafile = gdal.Open(img_fpath)
    try:
        if datafile.RasterXSize > 2048:
            return
    except Exception:
        return

    iftitle, ifext = re.match(r'(.*)\.(tiff|tif)', img_fpath).groups()
    step_x, step_y = tile_size

    xsize = datafile.RasterXSize
    ysize = datafile.RasterYSize

    for x in range(0, xsize, step_x):
        for y in range(0, ysize, step_y):
            gdal.Translate(
                f'{iftitle}.x{x}_y{y}.{ifext}',
                img_fpath,
                srcWin=[x, y, step_x, step_y],
                format="GTiff"
            )


def break_up_images(dir: str) -> None:
    """ Breaks an image down to 64 x 64 """
    dir_fpath = os.path.join(PROJECT_DIR, dir)
    IMG_FOLDER = re.compile(f'(.*){dir}(.*)')
    for root, dirs, imgs in os.walk(dir_fpath):
        for img in imgs:
            m = re.match(IMG_FOLDER, root)
            if not m:
                continue

            if img.endswith('.xml'):
                os.remove(img)

            _, folder = m.groups()
            try:
                img_path = os.path.join(root, img)
                make_tiles(dir, (dems, dems), img_path)
            except FileNotFoundError:
                pass

            try:
                os.remove(os.path.join(dir, folder, img))
            except FileNotFoundError:
                pass





def remove_64(folder: str) -> None:
    REGEX = re.compile(r"(.*)_([0-9]+).(.*).x([0-9]+)_y([0-9]+).tif")
    for root, dirs, files in os.walk(folder):
        for file in files:

            m = re.match(REGEX, file)
            if not m or not file.endswith('.tif'):
                continue
            os.remove(os.path.join(root, file))


def run_gui(folder: str, model) -> None:
    predictions, data_iter, metadata = test_model_masked(
        model, folder, True, dems=512
    )
    edit_predictions(
        predictions, data_iter, metadata, dem=512
    )


def main(folder: str) -> None:
    full_path = os.path.join("datasets", folder)
    model = load_model("AI_FCN_512")
    remove_64(full_path)
    run_gui(folder, model)
    print("Finishing up...")
    break_up_images(full_path)


if __name__ == "__main__":
    # TODO: Remove after done with testing
    p = ArgumentParser()
    p.add_argument("folder", help='folder containing data')
    # p.add_argument("power", help='Enter a power of two')

    args = p.parse_args()
    main(args.folder)
