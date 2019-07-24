#! /usr/bin/env python3
"""
Author: Rohan Weeden
    Helper script for tiling a GeoTiff, creating image labels, and for preparing
data to be used in the network.
## Annoying dependencies:
  * matplotlib
  * gdal
# Usage
First tile the image:
    `$ python3 tile_geotiff.py tile path/to/geo.tiff <size of tiles>`
Then classify the tiles:
    `$ python3 tile_geotiff.py classify path/to/`
"""

import json
import os
import random
import re
from argparse import ArgumentParser
from typing import Any, List, Tuple

from matplotlib.widgets import Button

import src.config as config
from src.dataset.common import gdal_open, valid_image
from src.plots import close_button, maximize_plot

try:
    from matplotlib import pyplot
    from matplotlib.widgets import RadioButtons
except ImportError:
    pass

try:
    import gdal
except ImportError:
    pass

EXT = "tiff|tif|TIFF|TIF"
FILENAME_REGEX = re.compile(f'.*_ulx_.*\\.(?:{EXT})')


def make_tiles(ifname: str, tile_size: Tuple[int, int]) -> None:
    """ Takes a .tiff file and breaks it into smaller .tiff files. """
    img_fpath = os.path.join(config.PROJECT_DIR, 'prep_tiles', ifname)

    if not check_dependencies(('gdal', )):
        return

    datafile = gdal.Open(img_fpath)
    iftitle, ifext = re.match(r'(.*)\.(tiff|tif)', img_fpath).groups()
    step_x, step_y = tile_size

    xsize = datafile.RasterXSize
    ysize = datafile.RasterYSize

    for x in range(0, xsize, step_x):
        for y in range(0, ysize, step_y):
            gdal.Translate(
                f'{iftitle}_ulx_{x}_uly_{y}.{ifext}',
                img_fpath,
                srcWin=[x, y, step_x, step_y],
                format="GTiff"
            )


def interactive_classifier(directory: str) -> None:
    if not check_dependencies(('gdal', 'matplotlib')):
        return

    try:
        with open(os.path.join(directory, 'labels.json'), 'r') as f:
            image_labels = json.load(f)
    except FileNotFoundError:
        image_labels = {}

    for file in os.listdir(directory):
        if not re.match(FILENAME_REGEX, file):
            continue
        current_label = image_labels.get(file)
        if current_label and current_label != 'skip':
            continue

        tif = gdal.Open(os.path.join(directory, file))
        tif_array = tif.ReadAsArray()
        print("Name: ", file)
        # Hack for signaling that the close button was clicked
        close = {"close": False}
        _show_plot(tif_array, file, image_labels, close)

        if close['close']:
            break

        with open(os.path.join(directory, 'labels.json'), 'w') as f:
            json.dump(image_labels, f)


def _show_plot(tif_array, file, image_labels, close):
    pyplot.imshow(tif_array, cmap=pyplot.get_cmap('gray'))
    pyplot.colorbar()
    rax = pyplot.axes([0.05, 0.7, 0.15, 0.15])
    classify_radio = RadioButtons(
        rax, ('Water', 'Not Water', 'Skip', 'Invalid')
    )
    bclose = Button(pyplot.axes([0.05, 0.05, 0.1, 0.075]), 'Close')

    def close_handler(event):
        close['close'] = True
        pyplot.close()

    bclose.on_clicked(close_handler)

    def click_handler(label: str):
        image_labels[file] = label.lower().replace(' ', '_')
        pyplot.close()

    classify_radio.on_clicked(click_handler)

    mng = pyplot.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    pyplot.show()


def prepare_data(directory: str, holdout: float):
    """ Moves images to the correct directory structure. """
    try:
        with open(os.path.join(directory, 'labels.json'), 'r') as f:
            image_labels = json.load(f)
    except FileNotFoundError:
        prepare_mask_data(directory, holdout)
        return

    file_names = list(
        filter(
            lambda x: re.match(FILENAME_REGEX, x) is not None,
            os.listdir(directory)
        )
    )

    for file in file_names:
        if file not in image_labels:
            continue

        test_or_train = 'train' if random.random() > holdout else 'test'
        folder = os.path.join(directory, test_or_train)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        os.rename(os.path.join(directory, file), os.path.join(folder, file))


def prepare_mask_data(directory: str, holdout: float) -> None:
    """ Renames and moves mask and tile images. """
    TILE_REGEX = re.compile(f"Image_(.*)VH_([0-9]+)\\.({EXT})")

    for file in os.listdir(directory):
        m = re.match(TILE_REGEX, file)
        if not m:
            continue

        pre, num, ext = m.groups()
        new_vh_name = f"{pre}_{num}.tile.vh.{ext}".lower()
        mask_name = f"Mask_{pre}Mask_{num}.{ext}"
        new_mask_name = f"{pre}_{num}.mask.{ext}".lower()
        vv_name = f"Image_{pre}VV_{num}.{ext}"
        new_vv_name = f"{pre}_{num}.tile.vv.{ext}".lower()

        if not os.path.isfile(os.path.join(directory, mask_name)):
            print(f"Tile: {file} is missing a mask {mask_name}!")
            continue

        if not os.path.isfile(os.path.join(directory, vv_name)):
            print(f"Tile: {file} is missing {vv_name}!")
            continue

        test_or_train = 'train' if random.random() > holdout else 'test'

        folder = os.path.join(directory, test_or_train)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        os.rename(
            os.path.join(directory, file), os.path.join(folder, new_vh_name)
        )
        os.rename(
            os.path.join(directory, vv_name),
            os.path.join(folder, new_vv_name)
        )
        os.rename(
            os.path.join(directory, mask_name),
            os.path.join(folder, new_mask_name)
        )


def check_dependencies(deps: Tuple[str, ...]) -> bool:
    global_vars = globals()
    for dep in deps:
        if dep not in global_vars:
            print(
                f"This function requires {dep}. "
                "Please install it in the current shell and try again."
            )
            return False
    return True


def move_imgs(directory: str) -> None:
    """ Moves all images within each sub directory into one directory """
    f_path = os.path.join(config.DATASETS_DIR, args.directory)
    for root, directories, files in os.walk(f_path, topdown=False):
        for img in files:
            os.rename(
                os.path.join(root, img),
                os.path.join(f_path, img)
            )
        for name in directories:
            os.rmdir(os.path.join(root, name))


def groom_imgs(directory: str) -> None:
    VH_REGEX = re.compile(r"(.*)\.tile\.vh\.tif")
    f_path = os.path.join(config.DATASETS_DIR, args.directory)
    g_path = os.path.join(config.DATASETS_DIR, f'{args.directory}Groomed')

    done = False
    count = 0
    update_count = 0
    for root, directories, files in os.walk(f_path):
        for vh in files:
            if done:
                break
            m = re.match(VH_REGEX, vh)
            if not m:
                continue

            pre = m.group(1)
            mask = f"{pre}.mask.tif"
            vv = f"{pre}.tile.vv.tif"

            # Contains full path and the name for each image
            l_imgs = [
                (mask, os.path.join(root, mask)),
                (vh, os.path.join(root, vh)),
                (vv, os.path.join(root, vv))
            ]
            num_imgs = int(len(files) / 3)

            with gdal_open(os.path.join(root, vh)) as f:
                vh_array = f.ReadAsArray()
            if not valid_image(vh_array):
                update_count += 1
                delete_imgs(l_imgs)
                continue

            with gdal_open(os.path.join(root, vv)) as f:
                vv_array = f.ReadAsArray()
            if not valid_image(vv_array):
                update_count += 1
                delete_imgs(l_imgs)
                continue

            with gdal_open(os.path.join(root, mask)) as f:
                mask_array = f.ReadAsArray()

            count += 1
            pyplot.subplot(1, 3, 1)
            pyplot.title('mask: Water = Black    Land = White')
            pyplot.xlabel(f'On {count} of {num_imgs-update_count}')
            pyplot.imshow(
                mask_array, cmap=pyplot.get_cmap('gist_yarg')
            )

            pyplot.subplot(1, 3, 2)
            pyplot.title('vh')
            pyplot.xlabel(
                f'Remaining images: {num_imgs-count+1-update_count}'
            )
            flt = vh_array.flatten()
            mean = flt.mean()
            std = flt.std()
            vh_array = vh_array.clip(0, mean + 3 * std)
            pyplot.imshow(
                vh_array.reshape(512, 512), cmap=pyplot.get_cmap('gist_gray')
            )

            pyplot.subplot(1, 3, 3)
            pyplot.title('vv')

            flt = vh_array.flatten()
            mean = flt.mean()
            std = flt.std()
            vv_array = vv_array.clip(0, mean + 20 * std)
            pyplot.imshow(
                vv_array.reshape(512, 512), cmap=pyplot.get_cmap('gist_gray')
            )

            def close_plot(_: Any) -> None:
                nonlocal done
                done = True

            _cbtn = close_button(close_plot)
            _kpbtn = keep_button(g_path, l_imgs)
            _dbtn = delete_button(l_imgs)
            maximize_plot()
            pyplot.show()


def delete_button(imgs: List[str]) -> Button:
    """ Create a 'delete' button on the plot. Make sure to save this to a value.
    """
    button = Button(pyplot.axes([.175, 0.05, 0.1, 0.075]), 'Delete')

    def click_handler(event: Any) -> None:
        delete_imgs(imgs)
        pyplot.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def delete_imgs(imgs: List[str]) -> None:
    """ Deletes mask, vh, and vv images. """
    for i in range(3):
        os.remove(imgs[i][1])


def keep_button(g_path: str, imgs: List[str]) -> Button:
    """ Create a 'keep' button on the plot. Make sure to save this to a value.
    """
    TEST_REGEX = re.compile(r"(.*)test(.*)")
    if not os.path.isdir(g_path):
        os.mkdir(g_path)
        os.mkdir(os.path.join(g_path, 'test'))
        os.mkdir(os.path.join(g_path, 'train'))

    button = Button(pyplot.axes([.3, 0.05, 0.1, 0.075]), 'Keep')

    def click_handler(event: Any) -> None:
        m = re.match(TEST_REGEX, imgs[0][1])
        if not m:
            move_kept_imgs('train', g_path, imgs)
            pyplot.close()
        else:
            move_kept_imgs('test', g_path, imgs)
            pyplot.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def move_kept_imgs(folder: str, g_path: str, imgs: List[str]) -> None:
    """ Moves imgs with a good mask to a new folder. """
    for i in range(3):
        os.rename(
            imgs[i][1],
            os.path.join(g_path, os.path.join(folder, imgs[i][0]))
        )


if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # make_tiles
    parser_make_tiles = subparsers.add_parser(
        'tile', help='Tile a tiff into many smaller tiffs'
    )
    parser_make_tiles.add_argument("file_name")
    parser_make_tiles.add_argument(
        "tile_size", type=int, help='Side length/height of the square tiles'
    )

    def make_tiles_wrapper(args):
        make_tiles(args.file_name, (args.tile_size, args.tile_size))

    parser_make_tiles.set_defaults(func=make_tiles_wrapper)

    # interactive_classifier
    parser_classifier = subparsers.add_parser(
        'classify', help='Classify tiled images'
    )
    parser_classifier.add_argument("directory")

    def interactive_classifier_wrapper(args):
        interactive_classifier(args.directory)

    parser_classifier.set_defaults(func=interactive_classifier_wrapper)

    # prepare_data
    parser_prepare = subparsers.add_parser(
        'prepare',
        help='Prepare the data directory for use with `ImageGenerator.flow`'
    )
    parser_prepare.add_argument("directory")
    parser_prepare.add_argument(
        "holdout", type=float, help='Proportion of data to use for testing'
    )

    def prepare_data_wrapper(args):
        prepare_data(args.directory, args.holdout)

    parser_prepare.set_defaults(func=prepare_data_wrapper)

    # Moves images into one directory
    parser_move = subparsers.add_parser(
        'move',
        help='Moves all images within each sub directory into one directory'
    )
    parser_move.add_argument("directory")

    def move_imgs_wrapper(args):
        move_imgs(args.directory, args.name)

    parser_move.set_defaults(func=move_imgs)

    # Groom images
    parser_groom = subparsers.add_parser(
        'groom',
        help='Allows the user to delete all images that contain inaccurate water masks'
    )
    parser_groom.add_argument("directory")

    def grom_imgs_wrapper(args):
        groom_imgs(args.directory)

    parser_groom.set_defaults(func=groom_imgs)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
