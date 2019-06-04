"""
Alaska Satellite Facility
Convolutional Neural Network
McKade Sorensen (Douglas)
05/20/2019

This includes funtions that will set up the SAR data so that it can be correctly fed into the
Convoulutional Neural Network. It sets up all the directorys that you should need, if you don't
already have them. The only thing that needs to be done a user is to extract the images into
the dataset file and move the labels.json and asf_cnn.h5 into the AI_Project directory. Running
main.py once should create the AI_Project directory.
"""
import datetime
import json
import os as os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

# File Paths
CURRENT_DIRECTORY = os.getcwd()
AI_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project')
DATASET_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project/dataset')
WATER_TRAINING_DATA = os.path.join(CURRENT_DIRECTORY,
                                   'AI_Project/training_data/water')
NO_WATER_TRAINING_DATA = os.path.join(CURRENT_DIRECTORY,
                                      'AI_Project/training_data/no_water')
WATER_TEST_DATA = os.path.join(CURRENT_DIRECTORY, 'AI_Project/test_data/water')
NO_WATER_TEST_DATA = os.path.join(CURRENT_DIRECTORY, 'AI_Project/test_data/no_water')
WATER_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project/water')
NO_WATER_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project/no_water')
SKIP_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project/skip')
TRAINING_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project/training_data')
TEST_FPATH = os.path.join(CURRENT_DIRECTORY, 'AI_Project/test_data')
INCORRECT_PREDICTIONS_FPATH = os.path.join(CURRENT_DIRECTORY,
                                           'AI_Project/incorrect_predictions')
CNN_RESULTS = os.path.join(AI_FPATH, 'cnn_results')


def sar_data_setup():
    """This function renames the image with water, skip, not_water. It also moves the imgs
    into to folders based on if they have water or not and skip. """

    os.chdir(AI_FPATH)
    with open('labels.json') as sar_img:
        sar_data = json.load(sar_img)

    for index, image_name in enumerate(os.listdir("./dataset")):
        now = datetime.datetime.now()
        # Loop through the dataset
        label = sar_data[image_name]
        if label == 'skip' or label == 'invalid' and not image_name.startswith('skip'):
            os.rename(
                # Renames and moves the image to the proper directory
                os.path.join('dataset', image_name),
                os.path.join('skip', 'skip_' + str(index) + '_' + str(now) + '.tiff')
            )
        elif label == 'water' and not image_name.startswith('water'):
            os.rename(
                # Renames and moves the image to the proper directory
                os.path.join('dataset', image_name),
                os.path.join('water', 'water_' + str(index) + '_' + str(now) + '.tiff')
            )
        elif label == 'not_water' and not image_name.startswith('not_water'):
            os.rename(
                # Renames and moves the image to the proper directory
                os.path.join('dataset', image_name),
                os.path.join('no_water', 'not_water_' + str(index) + '_' + str(now) + '.tiff')
            )
        else:
            print('ERROR IN sar_data_setup')


def create_directories():
    """This function creates all the correct directorys within the users
    file system if they're not already created"""
    # Creating the directorys
    creating_file_directory(AI_FPATH, 'AI_Project', CURRENT_DIRECTORY)
    creating_file_directory(WATER_TEST_DATA, 'test_data/water', AI_FPATH)
    creating_file_directory(NO_WATER_TEST_DATA, 'test_data/no_water', AI_FPATH)
    creating_file_directory(WATER_TRAINING_DATA, 'training_data/water', AI_FPATH)
    creating_file_directory(NO_WATER_TRAINING_DATA, 'training_data/no_water', AI_FPATH)
    creating_file_directory(CNN_RESULTS, 'cnn_results', AI_FPATH)
    creating_file_directory(INCORRECT_PREDICTIONS_FPATH, 'incorrect_predictions', AI_FPATH)
    creating_file_directory(SKIP_FPATH, 'skip', AI_FPATH)
    creating_file_directory(WATER_FPATH, 'water', AI_FPATH)
    creating_file_directory(NO_WATER_FPATH, 'no_water', AI_FPATH)


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
    water_count = round(get_img_count(WATER_FPATH) * (percent_test_data*.01))
    no_water_count = round(get_img_count(NO_WATER_FPATH) * (percent_test_data*.01))

    # Moving the files from one file to the next
    # Test images
    moving_training_test_data(WATER_FPATH, WATER_TEST_DATA, water_count)
    moving_training_test_data(NO_WATER_FPATH, NO_WATER_TEST_DATA, no_water_count)

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
    moving_training_test_data(WATER_FPATH, WATER_TRAINING_DATA, water_count_training)
    moving_training_test_data(NO_WATER_FPATH, NO_WATER_TRAINING_DATA, no_water_count_training)


def moving_training_test_data(current_file_path, new_file_path, number):
    """This function moves the training and test data"""
    count = 0
    # Loops through current_file_path and moves the first images up to the the number given.
    for image_name in os.listdir(current_file_path):
        if count == number:
            break

        os.rename(
            os.path.join(current_file_path, image_name),
            os.path.join(new_file_path,  image_name)
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
    moving_training_test_data(WATER_TRAINING_DATA, WATER_FPATH, water_training_count)

    # No water
    moving_training_test_data(NO_WATER_TEST_DATA, NO_WATER_FPATH, no_water_test_count)
    moving_training_test_data(NO_WATER_TRAINING_DATA, NO_WATER_FPATH, no_water_training_count)


def move_incorrect_predictions(list_of_img_details={'img_name': '', 'status': '',
                                                    'prediction': '', 'percent': ''}):
    """Moves imgs that were incorrectly predicted to a folder"""
    for img in list_of_img_details:
        # Runs through the dictonary and looks for incorrect predictions
        if img['status'] != img['prediction']:
            if img['status'] == 'water':
                c_file_path = os.path.join(CURRENT_DIRECTORY,
                                           'AI_Project/test_data/water')
            elif img['status'] == 'no_water':
                c_file_path = os.path.join(CURRENT_DIRECTORY,
                                           'AI_Project/test_data/no_water')
            os.rename(
                # Renames and moves the image to the proper directory
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
                # Moves the image to the proper directory
                os.path.join(INCORRECT_PREDICTIONS_FPATH, img_name),
                os.path.join(WATER_TRAINING_DATA, img_name)
                )
        elif img_name.startswith('not_water'):
            os.rename(
                # Moves the image to the proper directory
                os.path.join(INCORRECT_PREDICTIONS_FPATH, img_name),
                os.path.join(NO_WATER_TRAINING_DATA, img_name)
            )
        else:
            print("ERROR IN move_incorrect_predictions_back")
            print(img_name)


def dictonary_pair_to_list(pair, list_of_img_details={'img_name': '', 'status': '',
                           'prediction': '', 'percent': ''}):
    """ Creates a list out of one of the dictonarys pairs"""
    returned_list = []
    for x in list_of_img_details:
        returned_list.append(x[pair])

    return returned_list


def plot_img_incorrect_pred(list_of_img_details={'img_name': '', 'status': '', 'prediction': '',
                                                 'percent': ''}):
    """Plots the imgs that were predicted incorrectly and saves them to a file. """
    prediction = ''
    status = ''
    percent = ''

    # These directories are created here instead of the create_directories() becuase the name
    # is dependent on the date and time.
    CNN_STATS_FILE = creating_file_directory(os.path.join(AI_FPATH, 'cnn_results/cnn_' +
                                             str(datetime.datetime.now())), 'cnn_' +
                                             str(datetime.datetime.now()),
                                             os.path.join(AI_FPATH, 'cnn_results'))
    CNN_INCORRECT_PLOTS = creating_file_directory(os.path.join(CNN_STATS_FILE, 'plots'),
                                                  'plots', CNN_STATS_FILE)

    for img_name in os.listdir(INCORRECT_PREDICTIONS_FPATH):
        os.chdir(INCORRECT_PREDICTIONS_FPATH)
        # Gets the percecent that the NN gave an image.
        # And saves the images to the given directory
        for x in list_of_img_details:
            if img_name == x['img_name']:
                percent = x['percent']

        if img_name.startswith('water'):
            prediction = 'no_water'
            status = 'water'
        elif img_name.startswith('not_water'):
            prediction = 'water'
            status = 'no_water'
        else:
            print("ERROR IN plot_img_incorrect_pred()")

        # Creating and saving incorrect photos as a png file
        img = mpimg.imread(os.path.join(INCORRECT_PREDICTIONS_FPATH, img_name))
        plt.imshow(img)
        plt.title('Prediction = ' + prediction + '  Solution = ' + status)
        plt.xlabel('Percent: ' + str(percent))
        plt.ylabel('Image: ' + img_name)
        plt.savefig(os.path.join(CNN_INCORRECT_PLOTS, img_name + '.png'))
        os.chdir(AI_FPATH)

    # Returns a file path so that the .csv file and .h5 can be saved to that file
    return CNN_STATS_FILE
