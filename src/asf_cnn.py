"""
Alaska Satellite Facility
Convolutional Neural Network
McKade Sorensen (Douglas)
05/16/2019

Detects water within a SAR image.

Part 1: Creating the CNN
Step 1: Convolution
Step 2: Max Pooling
Step 3: Flattening
Step 4: Full Connection - ANN

Part 2: Fitting the CNN to the image
"""

import os
import re
from typing import Any, Dict, List, Tuple

import numpy as np
from keras.models import Model

from .dataset import load_dataset
from .model import save_model
from .typing import ConfMatrix, History


def train_model(
    model: Model,
    model_history: History,
    dataset: str,
    epochs: int,
    verbose: int = 1
) -> None:
    if verbose > 0:
        model.summary()

    training_set, test_set = load_dataset(dataset)

    step_size_training = len(training_set)
    step_size_vaild = len(test_set)

    if not step_size_training:
        if verbose > 0:
            print("No training data! Aborting...")
            return

    # Get the number of existing entries in the history
    epoch_prev = len(next(iter(model_history.values())))

    for epoch in range(epochs):
        epoch += 1

        if verbose > 0:
            print(f"Epoch {epoch}/{epochs}")

        history = model.fit_generator(
            training_set,
            steps_per_epoch=step_size_training,
            epochs=1,
            validation_data=test_set,
            validation_steps=step_size_vaild,
            verbose=verbose
        )

        for key in model_history.keys():
            model_history[key] += history.history[key]

        save_model(model, f"e{epoch + epoch_prev}", history=model_history)

    save_model(model, 'latest')


def test_model(model: Model, dataset: str,
               verbose: int = 1) -> Tuple[Dict[str, List[Any]], ConfMatrix]:
    if verbose > 0:
        model.summary()

    _, test_iter, _, test_metadata = load_dataset(dataset, get_metadata=True)

    predictions = model.predict_generator(
        test_iter, steps=len(test_iter), verbose=verbose
    )
    test_iter.reset()

    total = 0
    total_correct = 0
    num_to_labels = {0: "not_water", 1: "water"}
    details: Dict[str, List[Any]] = {
        "Image": [],
        "Label": [],
        "Prediction": [],
        "Percent": []
    }

    # Test iter needs to have batch size of 1
    for prediction, (_, [label]), (image_name, _) in zip(
        predictions,
        test_iter,
        test_metadata,
    ):
        total += 1
        prediction = prediction[0]
        if label == round(prediction):
            total_correct += 1

        details["Image"].append(image_name)
        details["Label"].append(num_to_labels[label])
        details["Prediction"].append(num_to_labels[round(prediction)])
        details["Percent"].append(prediction)

    print(f"Computed accuracy: {total_correct/total}")

    # Compute a confusion chart
    test_iter.reset()
    totals_matrix = np.zeros((2, 2))    # Hardcoded number of predictions
    for prediction, (_, [label]) in zip(predictions, test_iter):
        actual = label
        prediction = int(round(prediction[0]))
        totals_matrix[actual][prediction] += 1

    confusion_matrix = totals_matrix / len(predictions)

    return details, confusion_matrix


def display_predictions(predictions: List[float], dataset: str):
    # TODO: Find a better home for this

    TILENAME_REGEX = re.compile(r'.*_(ulx_[0-9]+_uly_[0-9]+).*\.(?:tiff|tif)')

    _, test_iter, _, test_metadata = load_dataset(dataset, get_metadata=True)

    # Show all of the test samples
    from matplotlib import pyplot

    test_iter.reset()
    predict_iter = iter(predictions)
    meta_iter = iter(test_metadata)

    for i in range(len(test_iter) // 9):
        for j in range(9):
            # Test iter needs to have batch size of 1
            predicted, ([img], [label]), (image_name, _) = next(
                zip(predict_iter, test_iter, meta_iter)
            )
            m = re.match(TILENAME_REGEX, image_name)
            if m:
                image_name = m.group(1)
            pyplot.subplot(3, 3, j + 1)
            pyplot.imshow(
                img.reshape(512, 512), cmap=pyplot.get_cmap('gist_gray')
            )
            pyplot.text(512, 0, f"Actual: {label}")
            pyplot.text(512, 40, f"Predicted: {predicted:.4}")
            pyplot.title(os.path.basename(image_name))

        mng = pyplot.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        pyplot.show()
