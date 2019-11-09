import re
import os
from argparse import ArgumentParser

import src.config as config
from osgeo import gdal
from typing import Tuple


def make_tiles(ifname: str,
               tile_size: Tuple[int, int],
               folder: str) -> None:
    """ Takes a .tiff file and breaks it into smaller .tiff files. """

    img_fpath = os.path.join(config.PROJECT_DIR, ifname, folder)

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


def break_up_image(dir: str) -> None:
    """ Breaks an image down to 64 x 64 """
    dir_fpath = os.path.join(config.PROJECT_DIR, dir)
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
                print(f"img path: {img_path}")
                make_tiles(dir, (64, 64), img_path)
            except FileNotFoundError:
                pass

            try:
                os.remove(os.path.join(dir, folder, img))
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    break_down = sp.add_parser('break_down', help='Break an image down to 64x64')
    break_down.add_argument('folder', help='path to images')
    break_down.set_defaults(func=break_up_image)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args.folder)
    else:
        p.print_help()
