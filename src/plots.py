"""
Plots Neural Nets masked predictions
"""

import os
import re
from typing import Any, Callable, List, Optional

import pyperclip
from keras.preprocessing.image import Iterator
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

from mask_editor import interactive_editor
from scripts.identify_water import write_mask_to_file

from .config import DATASETS_DIR, NETWORK_DEMS
from .gdal_wrapper import gdal_open


def edit_predictions(
    predictions, test_iter: Iterator, dataset: List[str], dem=NETWORK_DEMS
) -> None:
    done = False
    REG_EX = re.compile(r'(.*)_(.*)/(train|test)(.*)')
    for pred, (img, mask), f_path in zip(predictions, test_iter, dataset):
        # Plots imgs from img_dict
        m = re.match(REG_EX, f_path[0])
        _, environment, _, _ = m.groups()
        if done:
            break

        plots(pred, mask, img, environment, dem=dem)

        def close_plot(_: Any) -> None:
            nonlocal done
            done = True

        _copy_btn = copy_img_name(f_path[0])
        _cbtn = close_button(close_plot)
        _kpbtn = keep_button(f_path)
        _rpbtn = replace_button(f_path, pred)
        _edit_m_btn = edit_mask_button(f_path)
        _edit_p_btn = edit_pred_button(f_path, pred)
        _dltbtn = delete_button(f_path)
        maximize_plot()

        plt.show()


def plot_predictions(
    predictions, test_iter: Iterator
) -> None:
    """ Plots the Neural Nets predictions, the mask images and sar images """
    done = False
    for pred, (img, mask) in zip(predictions, test_iter):
        # Plots imgs from img_dict
        if done:
            break

        plots(pred, mask, img)

        def close_plot(_: Any) -> None:
            nonlocal done
            done = True

        _cbtn = close_button(close_plot)
        maximize_plot()
        plt.show()


def plots(pred, mask, img, environment='', dem=NETWORK_DEMS) -> None:
    plt.subplot(1, 4, 1)
    plt.title('prediction')
    plt.xlabel(environment)
    plt.imshow(pred.reshape(dem, dem), cmap=plt.get_cmap('gist_gray'))

    plt.subplot(1, 4, 2)
    plt.title('mask')
    plt.imshow(mask.reshape(dem, dem), cmap=plt.get_cmap('gist_gray'))

    plt.subplot(1, 4, 3)
    plt.title('vh img')
    img = img.clip(0, 1)
    plt.imshow(img[0, :, :, 0].reshape(dem, dem),
               cmap=plt.get_cmap('gist_gray'))

    plt.subplot(1, 4, 4)
    plt.title('vv img')
    img = img.clip(0, 1)
    plt.imshow(img[0, :, :, 1].reshape(dem, dem),
               cmap=plt.get_cmap('gist_gray'))


def copy_img_name(f_path):
    button = Button(plt.axes([0.05, 0.15, 0.1, 0.075]), 'Copy')

    def click_handler(event: Any) -> None:
        REG_EX = re.compile(r'(.*)/(.*).vh.tif')
        m = re.match(REG_EX, f_path)
        _, img = m.groups()
        print(img)
        pyperclip.copy(img)

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def save_img(f_paths: List[str], pred, dem=NETWORK_DEMS) -> None:
    with gdal_open(f_paths[2]) as f:
        mask_projection = f.GetProjection()
        mask_geo_transform = f.GetGeoTransform()

    write_mask_to_file(
        pred.reshape(dem, dem), f_paths[2], mask_projection, mask_geo_transform
    )


def move_img(f_paths: List[str]) -> None:
    REG_EX = re.compile(f'{DATASETS_DIR}/(.*)/(.*)/(.*)')
    for imgs in f_paths:
        m = re.match(REG_EX, imgs)
        dataset_dir, t_dir, img = m.groups()
        groomed_dir = os.path.join(DATASETS_DIR, f'{dataset_dir}_Groomed')

        if not os.path.isdir(groomed_dir):
            os.mkdir(groomed_dir)
            os.mkdir(os.path.join(groomed_dir, 'test'))
            os.mkdir(os.path.join(groomed_dir, 'train'))

        os.rename(imgs, os.path.join(groomed_dir, t_dir, img))


# Buttons
def edit_mask_button(f_paths: List[str]) -> Button:
    button = Button(plt.axes([.3, 0.05, 0.1, 0.075]), 'edit mask')

    def click_handler(event: Any) -> None:
        plt.close()
        interactive_editor(f_paths[2])
        move_img(f_paths)

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def edit_pred_button(f_paths: List[str], pred) -> Button:
    button = Button(plt.axes([.175, 0.05, 0.1, 0.075]), 'edit prediction')

    def click_handler(event: Any) -> None:
        save_img(f_paths, pred)
        plt.close()
        interactive_editor(f_paths[2])
        move_img(f_paths)

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def delete_button(f_paths: List[str]) -> Button:
    button = Button(plt.axes([.675, 0.05, 0.1, 0.075]), 'delete')

    def click_handler(event: Any) -> None:
        for img in f_paths:
            os.remove(img)
        plt.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def keep_button(f_paths: List[str]) -> Button:
    button = Button(plt.axes([.55, 0.05, 0.1, 0.075]), 'keep')

    def click_handler(event: Any) -> None:
        move_img(f_paths)
        plt.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def replace_button(f_paths: List[str], pred) -> Button:
    button = Button(plt.axes([.425, 0.05, 0.1, 0.075]), 'replace')

    def click_handler(event: Any) -> None:
        save_img(f_paths, pred)
        move_img(f_paths)
        plt.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def maximize_plot() -> None:
    backend = plt.get_backend()
    mng = plt.get_current_fig_manager()

    backend_ = backend.lower()
    if backend_ == 'tkagg':
        if os.name == 'posix':
            mng.resize(*mng.window.maxsize())
        else:
            mng.window.state('zoomed')
    elif backend_ == 'wxagg':
        mng.frame.Maximize(True)
    elif re.match('qt[0-9]*agg', backend_):
        mng.window.showMaximized()
    else:
        raise RuntimeError(f"Backend {backend} is not supported")


def close_button(callback: Optional[Callable[[Any], None]] = None) -> object:
    """ Create a 'close' button on the plot. Make sure to save this to a value.
    """
    button = Button(plt.axes([0.05, 0.05, 0.1, 0.075]), 'Close')

    def click_handler(event: Any) -> None:
        if callback:
            callback(event)
        plt.close()

    button.on_clicked(click_handler)
    # Need to return the button to prevent it from being garbage collected
    return button
