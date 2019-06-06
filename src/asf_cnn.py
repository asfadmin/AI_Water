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

# import pandas as pd
from keras.models import Model

from . import img_functions
from .dataset import load_dataset
from .model import save_model
from .typing import History


def train_model(
    model: Model,
    model_history: History,
    dataset: str,
    epochs: int,
    verbose: int = 1
):
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


def test_model(model: Model, dataset: str, verbose: int = 1):
    training_set, test_set = load_dataset()

    step_size_vaild = len(test_set)
    step_size_test = step_size_vaild

    # Code below sets up stats on how the CNN did
    model.evaluate_generator(generator=test_set, steps=step_size_vaild)
    test_set.reset()
    percent_of_pred = model.predict_generator(
        test_set, steps=step_size_test, verbose=1
    )

    list_pred = []
    list_of_img_details = []

    percent_of_pred *= 100
    for x in percent_of_pred:
        # Pulls the predictions and adds it to a dictonary to be stored in a list.
        # Also gives the percent that it is certain it got it right.
        if x >= 50:
            value = 'water'
        else:
            value = 'no_water'

        list_pred.append(value)

    index = 0
    for file_name in os.listdir(test_fpath):
        # This loop creates a dictonary with all a images stats.
        for img_name in os.listdir(os.path.join(test_fpath, file_name)):
            details_of_img = {
                'img_name': img_name,
                'status': '',
                'prediction': list_pred[index],
                'percent': percent_of_pred[index]
            }
            if img_name.startswith('water'):
                details_of_img['status'] = 'water'
            elif img_name.startswith('not_water'):
                details_of_img['status'] = 'no_water'
            else:
                print('ERROR WITH IMAGE DATA')

            list_of_img_details.append(details_of_img)
            index += 1

    img_functions.move_incorrect_predictions(list_of_img_details)

    # Pulling the data from the list to put into a .csv file.
    img_names_list = img_functions.dictonary_pair_to_list(
        'img_name', list_of_img_details
    )
    img_status = img_functions.dictonary_pair_to_list(
        'status', list_of_img_details
    )
    results = pd.DataFrame({
        "Images": img_names_list,
        "Status": img_status,
        "Predictions": list_pred,
        "Percent": list(percent_of_pred)
    })
    CNN_STATS_FILE = img_functions.plot_img_incorrect_pred(list_of_img_details)
    img_functions.move_incorrect_predictions_back()

    results.to_csv(os.path.join(CNN_STATS_FILE, "results.csv"), index=True)

    # Saving the model
    model.save('asf_cnn.h5')
    model.save(os.path.join(CNN_STATS_FILE, 'asf_cnn.h5'))
    # Opens all the directory with all the stats so that the user can view them.
    os.system(f'xdg-open "{CNN_STATS_FILE}"')
