"""
Alaska Satellite Facility
Convolutional Neural Network
McKade Sorensen (Douglas)
05/20/2019

This includes functions that will set up the SAR data so that it can be
correctly fed into the Convoulutional Neural Network. It sets up all the
directories that you should need, if you don't already have them. The only
thing that needs to be done a user is to extract the images into the dataset
file and move the labels.json and asf_cnn.h5 into the AI_Project directory.
Running main.py once should create the AI_Project directory.
"""

import datetime
import json
import os as os
import re
from typing import Any, Callable, List, Optional

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from .config import PROJECT_DIR

# File Paths
CURRENT_DIRECTORY = PROJECT_DIR
DATASET_FPATH = os.path.join(CURRENT_DIRECTORY, 'dataset')
WATER_TRAINING_DATA = os.path.join(CURRENT_DIRECTORY, 'training_data/water')
NO_WATER_TRAINING_DATA = os.path.join(
    CURRENT_DIRECTORY, 'training_data/no_water'
)
WATER_TEST_DATA = os.path.join(CURRENT_DIRECTORY, 'test_data/water')
NO_WATER_TEST_DATA = os.path.join(CURRENT_DIRECTORY, 'test_data/no_water')
WATER_FPATH = os.path.join(CURRENT_DIRECTORY, 'water')
NO_WATER_FPATH = os.path.join(CURRENT_DIRECTORY, 'no_water')
SKIP_FPATH = os.path.join(CURRENT_DIRECTORY, 'skip')
TRAINING_FPATH = os.path.join(CURRENT_DIRECTORY, 'training_data')
TEST_FPATH = os.path.join(CURRENT_DIRECTORY, 'test_data')
INCORRECT_PREDICTIONS_FPATH = os.path.join(
    CURRENT_DIRECTORY, 'incorrect_predictions'
)
CNN_RESULTS = os.path.join(CURRENT_DIRECTORY, 'cnn_results')


def sar_data_setup():
    """This function renames the image with water, skip, not_water. It also moves the imgs
    into to folders based on if they have water or not and skip. """

    os.chdir(CURRENT_DIRECTORY)
    with open('labels.json') as sar_img:
        sar_data = json.load(sar_img)

    for index, image_name in enumerate(os.listdir("./dataset")):
        now = datetime.datetime.now()
        # Loop through the dataset
        label = sar_data[image_name]
        if label == 'skip' or label == 'invalid' and not image_name.startswith(
            'skip'
        ):
            os.rename(
                os.path.join('dataset', image_name),
                os.path.join(
                    'skip', 'skip_' + str(index) + '_' + str(now) + '.tiff'
                )
            )
        elif label == 'water' and not image_name.startswith('water'):
            os.rename(
                os.path.join('dataset', image_name),
                os.path.join(
                    'water', 'water_' + str(index) + '_' + str(now) + '.tiff'
                )
            )
        elif label == 'not_water' and not image_name.startswith('not_water'):
            os.rename(
                os.path.join('dataset', image_name),
                os.path.join(
                    'no_water',
                    'not_water_' + str(index) + '_' + str(now) + '.tiff'
                )
            )
        else:
            print('ERROR IN sar_data_setup')


def create_directories():
    """This function creates all the correct directorys within the users
    file system if they're not already created"""
    # Creating the directorys
    creating_file_directory(
        WATER_TEST_DATA, 'test_data/water', CURRENT_DIRECTORY
    )
    creating_file_directory(
        NO_WATER_TEST_DATA, 'test_data/no_water', CURRENT_DIRECTORY
    )
    creating_file_directory(
        WATER_TRAINING_DATA, 'training_data/water', CURRENT_DIRECTORY
    )
    creating_file_directory(
        NO_WATER_TRAINING_DATA, 'training_data/no_water', CURRENT_DIRECTORY
    )
    creating_file_directory(CNN_RESULTS, 'cnn_results', CURRENT_DIRECTORY)
    creating_file_directory(
        INCORRECT_PREDICTIONS_FPATH, 'incorrect_predictions', CURRENT_DIRECTORY
    )
    creating_file_directory(SKIP_FPATH, 'skip', CURRENT_DIRECTORY)
    creating_file_directory(WATER_FPATH, 'water', CURRENT_DIRECTORY)
    creating_file_directory(NO_WATER_FPATH, 'no_water', CURRENT_DIRECTORY)


def creating_file_directory(file_path, file_name, directory):
    """This funtion takes in a path and file name, if the path isn't their it will
    create it with the path with the given name. The third parameter is the directory you
    want the new file to go. """

    if os.path.isdir(file_path) is False:
        os.chdir(directory)
        os.makedirs(file_name)
    return os.path.join(directory, file_name)


def get_img_count(file_path):
    """ Gets the count of imgs in a file and returns it. """
    count = 0
    for image_water in os.listdir(file_path):
        count += 1
    return count


def test_training_data_percent(percent_test_data=''):
    """This function will take in a parameter that ask the percent
    of the data you want to be test data then calls a function to move
    both the training data and the test data."""
    # Getting the number of test/training images to move.
    water_count = round(get_img_count(WATER_FPATH) * (percent_test_data * .01))
    no_water_count = round(
        get_img_count(NO_WATER_FPATH) * (percent_test_data * .01)
    )

    # Moving the files from one file to the next
    # Test images
    moving_training_test_data(WATER_FPATH, WATER_TEST_DATA, water_count)
    moving_training_test_data(
        NO_WATER_FPATH, NO_WATER_TEST_DATA, no_water_count
    )

    # CODE Below will help create a 50/50 split in testing images.
    # comment out the function call of the larger data set above.
    # for index, img_name in enumerate(os.listdir(PUT FILE PATH OF LARGER DATA SET HERE)):
    #     if index == water_count:
    #         break
    #     os.rename(
    #         os.path.join(NO_WATER_FPATH, img_name),
    #         os.path.join(NO_WATER_TEST_DATA, img_name)
    #     )

    # Training images
    water_count_training = get_img_count(WATER_FPATH)
    no_water_count_training = get_img_count(NO_WATER_FPATH)
    moving_training_test_data(
        WATER_FPATH, WATER_TRAINING_DATA, water_count_training
    )
    moving_training_test_data(
        NO_WATER_FPATH, NO_WATER_TRAINING_DATA, no_water_count_training
    )


def moving_training_test_data(current_file_path, new_file_path, number):
    """This function moves the training and test data"""
    count = 0
    # Loops through current_file_path and moves the first images up to the the number given.
    for image_name in os.listdir(current_file_path):
        if count == number:
            break

        os.rename(
            os.path.join(current_file_path, image_name),
            os.path.join(new_file_path, image_name)
        )
        count += 1


def move_data_back():
    """ This function moves the images back to the proper directory to rerun the program """

    # Getting counts
    water_test_count = get_img_count(WATER_TEST_DATA)
    no_water_test_count = get_img_count(NO_WATER_TEST_DATA)
    water_training_count = get_img_count(WATER_TRAINING_DATA)
    no_water_training_count = get_img_count(NO_WATER_TRAINING_DATA)

    # Water
    moving_training_test_data(WATER_TEST_DATA, WATER_FPATH, water_test_count)
    moving_training_test_data(
        WATER_TRAINING_DATA, WATER_FPATH, water_training_count
    )

    # No water
    moving_training_test_data(
        NO_WATER_TEST_DATA, NO_WATER_FPATH, no_water_test_count
    )
    moving_training_test_data(
        NO_WATER_TRAINING_DATA, NO_WATER_FPATH, no_water_training_count
    )


def move_incorrect_predictions(
    list_of_img_details={
        'img_name': '',
        'status': '',
        'prediction': '',
        'percent': ''
    }
):
    """Moves imgs that were incorrectly predicted to a folder"""
    for img in list_of_img_details:
        # Runs through the dictonary and looks for incorrect predictions
        if img['status'] != img['prediction']:
            if img['status'] == 'water':
                c_file_path = os.path.join(CURRENT_DIRECTORY, 'test_data/water')
            elif img['status'] == 'no_water':
                c_file_path = os.path.join(
                    CURRENT_DIRECTORY, 'test_data/no_water'
                )
            os.rename(
                os.path.join(c_file_path, img['img_name']),
                os.path.join('incorrect_predictions', img['img_name'])
            )


def get_file_root():
    """ Allows other modules to access the home directory for this project."""
    print("This is the current file directory" + CURRENT_DIRECTORY)
    return CURRENT_DIRECTORY


def move_incorrect_predictions_back():
    """This function moves the incorrect functions to their right place"""
    for img_name in os.listdir(INCORRECT_PREDICTIONS_FPATH):
        if img_name.startswith('water'):
            os.rename(
                os.path.join(INCORRECT_PREDICTIONS_FPATH, img_name),
                os.path.join(WATER_TRAINING_DATA, img_name)
            )
        elif img_name.startswith('not_water'):
            os.rename(
                os.path.join(INCORRECT_PREDICTIONS_FPATH, img_name),
                os.path.join(NO_WATER_TRAINING_DATA, img_name)
            )
        else:
            print("ERROR IN move_incorrect_predictions_back")
            print(img_name)


def dictonary_pair_to_list(
    pair,
    list_of_img_details={
        'img_name': '',
        'status': '',
        'prediction': '',
        'percent': ''
    }
):
    """ Creates a list out of one of the dictonarys pairs"""
    returned_list = []
    for x in list_of_img_details:
        returned_list.append(x[pair])

    return returned_list


def save_incorrect_predictions(current_directory, predictions: List[float], dataset: str) -> None:

        TILENAME_REGEX = re.compile(r'.*_(ulx_[0-9]+_uly_[0-9]+).*\.(?:tiff|tif)')

        _, test_iter, _, test_metadata = load_dataset(dataset, get_metadata=True)
        _, num_to_label = make_label_conversions(dataset, {"water", "not_water"})

        # Show all of the test samples
        test_iter.reset()
        predict_iter = iter(predictions)
        meta_iter = iter(test_metadata)

        done = False
        for i in range(len(test_iter) // 9):
            if done:
                break
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

            pyplot.savefig(os.path.join(current_directory, i + '.png'))
