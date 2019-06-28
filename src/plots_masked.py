"""
Plots Neural Nets masked predictions
"""
import os
import re
from typing import List

import numpy as np
from matplotlib import pyplot
from matplotlib.widgets import Button

from .dataset.mask import load_dataset
from .dataset.common import dataset_dir

def plot_predictions(mask_pixel_preds, dataset: str) -> None:
    print('DELETE WHEN DONE plot_predictions **************************')
    MASK_TILE_REGEX = re.compile(r"(.*)_([0-9]+)_([0-9]+).mask.tif")

    mask_img_names = []
    tile_img_names = []
    for img_name in os.listdir(dataset_dir(os.path.join(dataset, 'test'))):
        m = re.match(MASK_TILE_REGEX, img_name)

        if not m:
            tile_img_names.append(img_name)
            continue
        mask_img_names.append(img_name)

    height = len(mask_pixel_preds)/512

    print(f'Image: {tile_img_names[0]}')
    for height in range(0, 512):
        for width in range(0, 512):
            print(mask_pixel_preds[width], end = '')
        print('')
