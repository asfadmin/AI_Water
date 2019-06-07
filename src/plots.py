import os
import re
from typing import List

import numpy as np
from matplotlib import pyplot

from .dataset import load_dataset, make_label_conversions


def plot_confusion_chart(confusion_matrix: np.ndarray) -> None:
    width, height = confusion_matrix.shape
    for x in range(width):
        for y in range(height):
            pyplot.annotate(
                str(confusion_matrix[x][y]),
                xy=(y, x),
                horizontalalignment='center',
                verticalalignment='center'
            )

    pyplot.imshow(confusion_matrix, cmap=pyplot.get_cmap('RdBu'))
    pyplot.xlabel("Actual")
    pyplot.ylabel("Predicted")
    pyplot.xticks(range(width))
    pyplot.yticks(range(height))
    pyplot.colorbar()
    pyplot.show()


def plot_predictions(predictions: List[float], dataset: str) -> None:
    TILENAME_REGEX = re.compile(r'.*_(ulx_[0-9]+_uly_[0-9]+).*\.(?:tiff|tif)')

    _, test_iter, _, test_metadata = load_dataset(dataset, get_metadata=True)
    _, num_to_label = make_label_conversions(dataset, {"water", "not_water"})

    # Show all of the test samples
    test_iter.reset()
    predict_iter = iter(predictions)
    meta_iter = iter(test_metadata)

    for i in range(len(test_iter) // 9):
        for j in range(9):
            # Test iter needs to have batch size of 1
            predicted, ([img], [label]), (image_name, _) = next(
                zip(predict_iter, test_iter, meta_iter)
            )
            label_text = num_to_label[label]
            predicted_text = num_to_label[int(round(predicted))]
            m = re.match(TILENAME_REGEX, image_name)
            if m:
                image_name = m.group(1)
            pyplot.subplot(3, 3, j + 1)
            pyplot.imshow(
                img.reshape(512, 512), cmap=pyplot.get_cmap('gist_gray')
            )
            y = 0

            def add_text(text, **kwargs) -> None:
                nonlocal y
                pyplot.text(540, y, text, **kwargs)
                y += 50

            add_text(f"Actual: {label_text} [{label}]")
            add_text(f"Predicted: {predicted_text} [{predicted:.4}]")
            verification_text, verification_color = {
                ('water', 'water'): ('True Positive', 'green'),
                ('water', 'not_water'): ('False Negative', 'red'),
                ('not_water', 'not_water'): ('True Negative', 'green'),
                ('not_water', 'water'): ('False Positive', 'red'),
            }.get((label_text, predicted_text), ("Unknown", 'yellow'))
            add_text(
                verification_text,
                bbox={
                    "facecolor": verification_color,
                    "alpha": 0.5
                }
            )
            pyplot.title(os.path.basename(image_name))

        maximize_plot()
        pyplot.show()


def maximize_plot() -> None:
    backend = pyplot.get_backend()
    mng = pyplot.get_current_fig_manager()

    if backend == 'TkAgg':
        if os.name == 'posix':
            mng.resize(*mng.window.maxsize())
        else:
            mng.window.state('zoomed')
    elif backend == 'wxAgg':
        mng.frame.Maximize(True)
    elif 'QT' in backend:
        mng.window.showMaximized()
    else:
        raise RuntimeError(f"Backend {backend} is not supported")
