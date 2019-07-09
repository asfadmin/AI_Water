"""
Plots Neural Nets masked predictions
"""

from typing import Any

from keras.preprocessing.image import Iterator
from matplotlib import pyplot as plt

from .plots import close_button, maximize_plot


def plot_predictions(predictions, test_iter: Iterator, dataset: str) -> None:
    """ Plots the Neural Nets predictions, the mask images and sar images """

    done = False
    for pred, (img, mask) in zip(predictions, test_iter):
        # Plots imgs from img_dict
        if done:
            break
        plt.subplot(1, 3, 1)
        plt.title('prediction')
        plt.imshow(pred.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 3, 2)
        plt.title('mask')
        plt.imshow(mask.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 3, 3)
        plt.title('img')
        plt.imshow(img.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        def close_plot(_: Any) -> None:
            nonlocal done
            done = True
        _cbtn = close_button(close_plot)
        maximize_plot()
        plt.show()
