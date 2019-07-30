"""
Plots Neural Nets masked predictions
"""

from typing import Any, List

from keras.preprocessing.image import Iterator
from matplotlib import pyplot as plt
from matplotlib.widgets import Button

from identify_water import write_mask_to_file

from .gdal_wrapper import gdal_open
from .plots import close_button, maximize_plot


def plot_predictions(
    predictions, test_iter: Iterator, dataset: List[str], t_f: bool
) -> None:
    """ Plots the Neural Nets predictions, the mask images and sar images """

    done = False
    for pred, (img, mask), f_path in zip(predictions, test_iter, dataset):
        # Plots imgs from img_dict
        if done:
            break
        plt.subplot(1, 4, 1)
        plt.title('prediction')
        plt.imshow(pred.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 4, 2)
        plt.title('mask')
        plt.imshow(mask.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 4, 3)
        plt.title('vh img')
        img = img.clip(0, 1)
        plt.imshow(img[0, :, :, 0].reshape(512, 512),
                   cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 4, 4)
        plt.title('vv img')
        img = img.clip(0, 1)
        plt.imshow(img[0, :, :, 1].reshape(512, 512),
                   cmap=plt.get_cmap('gist_gray'))

        def close_plot(_: Any) -> None:
            nonlocal done
            done = True

        if t_f is True:
            _cbtn = close_button(close_plot)
            _kpbtn = keep_button()
            _rpbtn = replace_button(f_path[2], pred)
            maximize_plot()
            plt.show()
        else:
            _cbtn = close_button(close_plot)
            maximize_plot()
            plt.show()


def keep_button() -> Button:
    button = Button(plt.axes([.175, 0.05, 0.1, 0.075]), 'keep')

    def click_handler(event: Any) -> None:
        plt.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button


def replace_button(f_path: str, pred) -> Button:
    button = Button(plt.axes([.3, 0.05, 0.1, 0.075]), 'replace')

    def click_handler(event: Any) -> None:
        with gdal_open(f_path) as f:
            mask_projection = f.GetProjection()
            mask_geo_transform = f.GetGeoTransform()

        write_mask_to_file(
            pred.reshape(512, 512), f_path, mask_projection, mask_geo_transform
        )
        plt.close()

    button.on_clicked(click_handler)
    # Returns to prevent the button from being garbage collected
    return button
