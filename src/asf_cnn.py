"""
asf_cnn.py contains the code that connects the Keras library with asf
written code.
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from keras.models import Model

from .dataset.binary import load_dataset as load_dataset_binary
from .dataset.binary import make_label_conversions
from .dataset.mask import load_dataset as load_dataset_masked
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
    if model_type(model) == ModelType.BINARY:
        training_set, test_set = load_dataset_binary(dataset)
    elif model_type(model) == ModelType.MASKED:
        training_set, test_set = load_dataset_masked(dataset)
    else:
        print(
            "Unknown model output shape. Expected either a binary"
            "classification model or a 512x512 pixel mask."
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


# Rename to test_binary_model
def test_model(model: Model, dataset: str,
               verbose: int = 1) -> Tuple[Dict[str, List[Any]], np.ndarray]:
    if verbose > 0:
        model.summary()

    if model_type(model) != ModelType.BINARY:
        raise NotImplementedError(
            "Model analysis is only supported for binary output"
        )

    _, test_iter, _, test_metadata = load_dataset_binary(
        dataset, get_metadata=True
    )

    predictions = model.predict_generator(
        test_iter, steps=len(test_iter), verbose=verbose
    )
    test_iter.reset()

    total = 0
    total_correct = 0
    _, num_to_label = make_label_conversions(dataset, {"water", "not_water"})

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
        details["Label"].append(num_to_label[label])
        details["Prediction"].append(num_to_label[round(prediction)])
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


def test_masked_model(model: Model, dataset: str,
                      verbose: int = 1):
    model
    if verbose > 0:
        model.summary()

    if model_type(model) != ModelType.MASKED:
        raise NotImplementedError("ERROR: With masked output")

    _, test_iter = load_dataset_masked(dataset)
    predictions = model.predict_generator(test_iter, len(test_iter),
                                          verbose=verbose)
    test_iter.reset()
    binary_predictions = predictions.round(decimals=0, out=None)

    return binary_predictions
