"""
Plots Neural Nets masked predictions
"""
import os
import re
from typing import Any

from matplotlib import pyplot as plt
from osgeo import gdal

from .dataset.common import dataset_dir
from .plots import close_button, maximize_plot


def plot_predictions(predictions, dataset: str) -> None:
    MASK_TILE_REGEX = re.compile(r"(.*)_([0-9]+)_([0-9]+).mask.tif")
    TEST_DIRECTORY = os.path.join(dataset_dir(dataset), 'test')

    list_sar_names = []
    list_mask_names = []
    for img_name in os.listdir(TEST_DIRECTORY):
        # Saving the mask imgs and tile imgs to lists
        m = re.match(MASK_TILE_REGEX, img_name)
        if not m:
            list_sar_names.append(img_name)
            continue
        list_mask_names.append(img_name)

    list_sar_names.sort()
    list_mask_names.sort()

    three_types_images = []
    for index, img in enumerate(predictions):
        # Plots prediction, mask, and rtc sar image.
        img_dict = {'prediction': img, 'mask': list_mask_names[index],
                    'sar': list_sar_names[index]}
        three_types_images.append(img_dict)

    done = False
    for dict in three_types_images:
        # Plots imgs from img_dict
        if done:
            break
        for index, img in enumerate(dict):
            plt.subplot(1, 3, index+1)
            if index == 0:
                plt.title('prediction')
                plt.imshow(dict[img].reshape(512, 512),
                           cmap=plt.get_cmap('gist_gray'))
            else:
                plt.title(dict[img])
                tif = gdal.Open(os.path.join(TEST_DIRECTORY, dict[img]))

                try:
                    tif_array = tif.ReadAsArray()
                except AttributeError:
                    'ERROR: plots_masked.py'

                tif_array = tif_array.clip(0, 1)
                plt.imshow(tif_array.reshape(512, 512),
                           cmap=plt.get_cmap('gist_gray'))

        def close_plot(_: Any) -> None:
            nonlocal done
            done = True
        _cbtn = close_button(close_plot)
        maximize_plot()
        plt.show()
