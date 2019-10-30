"""
asf_cnn.py contains the code that connects the Keras library with asf
written code.
"""

from typing import Tuple

import numpy as np
from keras.models import Model
from keras.preprocessing.image import Iterator

from .dataset.masked import load_dataset as load_dataset_masked
from .dataset.masked import load_replace_data
from .model import ModelType, model_type, save_model
from .typing import History


def train_model(
    model: Model,
    model_history: History,
    dataset: str,
    epochs: int,
    verbose: int = 1
) -> None:
    if verbose > 0:
        model.summary()

    if model_type(model) == ModelType.MASKED:
        training_set, test_set = load_dataset_masked(dataset)
    else:
        print(
            "Unknown model output shape."
        )
        return

    step_size_training = len(training_set)
    step_size_vaild = len(test_set)

    if not step_size_training:
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


def test_model_masked(
    model: Model,
    dataset: str,
    edit: bool,
    verbose: int = 1
) -> Tuple[np.ndarray, Iterator]:

    assert model_type(
        model
    ) == ModelType.MASKED, "This function only works on masked models"

    if verbose > 0:
        model.summary()

    if edit:
        dataset_data = load_replace_data(dataset)

        predictions = model.predict_generator(
            dataset_data[0], len(dataset_data[0]), verbose=verbose
        )
        dataset_data[0].reset()
        masked_predictions = predictions.round(decimals=0, out=None)

        return masked_predictions, dataset_data[0], dataset_data[1]

    else:
        _, test_iter = load_dataset_masked(dataset)
        predictions = model.predict_generator(
            test_iter, len(test_iter), verbose=verbose
        )
        test_iter.reset()
        masked_predictions = predictions.round(decimals=0, out=None)

        return masked_predictions, test_iter
