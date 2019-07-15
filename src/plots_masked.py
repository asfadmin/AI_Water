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
        plt.subplot(1, 4, 1)
        plt.title('prediction')
        plt.imshow(pred.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 4, 2)
        plt.title('mask')
        plt.imshow(mask.reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        # TODO: Get vh and vv image to compare
        plt.subplot(1, 4, 3)
        plt.title('vh img')
        img = img.clip(0, 1)
<<<<<<< HEAD
        plt.imshow(img[0, :, :, 0].reshape(512, 512),
                   cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 4, 4)
        plt.title('vv img')
        img = img.clip(0, 1)
        plt.imshow(img[0, :, :, 1].reshape(512, 512),
                   cmap=plt.get_cmap('gist_gray'))
=======
        print(img.shape)
        plt.imshow(img[0, :, :, 0].reshape(512, 512), cmap=plt.get_cmap('gist_gray'))

        plt.subplot(1, 4, 4)
        plt.title('vv img')
        # img = img.clip(0, 1)
        print(img.shape)
        plt.imshow(img[0, :, :, 1].reshape(512, 512), cmap=plt.get_cmap('gist_gray'))
>>>>>>> a42d5dabbcdf2f1f0ff78e96254bfda41c447958

        def close_plot(_: Any) -> None:
            nonlocal done
            done = True
        _cbtn = close_button(close_plot)
        maximize_plot()
        plt.show()
