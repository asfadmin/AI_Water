"""
Alaska Satellite Facility
Convolutional Neural Network
McKade Sorensen (Douglas)
05/21/2019

main.py, runs the code for AI_Project. The first time the program runs it'll create the files
needed. After its ran once the dataset folder (with all the SAR images) needs to be extracted into
AI_Project. asf_cnn.h5 and labels.json both need to be moved there into the AI_Project folder.
"""

import os

import asf_cnn as cnn
import img_functions


def main():
    # Passing the file directory main.py is located to be used for the rest of the program
    img_functions.create_directories()
    img_functions.move_incorrect_predictions_back()
    img_functions.move_data_back()
    # Setting up SAR data
    img_functions.sar_data_setup()
    # The paramerter is the percent of the data that is going to be test data.
    img_functions.test_training_data_percent(30)
    # Creating and running the CNN.
    cnn.cnn()
    img_functions.move_data_back()
    img_functions.move_incorrect_predictions_back()


def main_file_directory():
    """Returns main.py working directory"""
    return (os.path.dirname(os.path.abspath(__file__)))


if __name__ == '__main__':
    main()
