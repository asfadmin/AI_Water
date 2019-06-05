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

import pandas as pd
from keras.initializers import glorot_uniform
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Sequential, load_model
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import CustomObjectScope

import img_functions


def cnn():

    # Part 1: Creating the CNN
    # Initialising the CNN
    classifier = Sequential()

    # Step 1: Convolution
    # 1st parameter is number of filters, 2nd is filter size (x^2), 3rd = stride
    # 4th parameter is the expected format of the input images. The first two
    # parameters within that parameter are the dimensions (x and y) and the
    # last is color options. Color = 3, B/W = 1
    # 5th parameter is the activation function
    classifier.add(Conv2D(64, (3, 3), strides=(3, 3), input_shape=(512, 512, 1), activation='relu'))
    classifier.add(Conv2D(128, (3, 3), strides=(3, 3), input_shape=(512, 512, 1),
                   activation='relu'))
    # Step 2: Pooling (Max)
    # 1st parameter inside of MaxPooling2D is the gird size.
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    # Step 2.5 More Convo layers
    classifier.add(Conv2D(128, (3, 3), strides=(3, 3), input_shape=(512, 512, 1),
                          activation='relu'))
    classifier.add(Conv2D(128, (3, 3), strides=(3, 3), input_shape=(512, 512, 1),
                          activation='relu'))
    classifier.add(MaxPooling2D(pool_size=(2, 2)))
    # Step 3: Flattening
    classifier.add(Flatten())
    # Step 4: Full Connection
    # 1st parameter is the amount of nodes (Neurons)
    # 2nd parameter is the activation function
    classifier.add(Dense(units=128, activation='relu'))
    classifier.add(Dropout(rate=.5))
    classifier.add(Dense(units=128, activation='relu'))
    classifier.add(Dropout(rate=.5))
    classifier.add(Dense(units=64, activation='relu'))
    classifier.add(Dropout(rate=.3))
    classifier.add(Dense(units=1, activation='sigmoid'))

    # Compiling the CNN
    # 1st parameter is the optimizer.
    # 2nd parameter is the loss function
    # 3rd parameter is the performance metric
    # UNCOMMENT IF TRAINING IS BEING RESTARTED
    # classifier.compile('adam', loss='binary_crossentropy', metrics=['accuracy'])
    # COMMENT OUT IF TRAINING IS BEING RESTARTED
    CURRENT_DIRECTORY = img_functions.get_file_root()
    with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
        classifier = load_model(os.path.join(CURRENT_DIRECTORY, 'asf_cnn.h5'))
    classifier.summary()

    # File paths for grabbing the images.
    training_fpath = os.path.join(CURRENT_DIRECTORY, 'training_data')
    test_fpath = os.path.join(CURRENT_DIRECTORY, 'test_data')
    print(CURRENT_DIRECTORY)

    # Part 2: Fitting the CNN to the image
    # Implementing data augmentation, creates more images from given images.
    train_datagen = ImageDataGenerator(
            rescale=1./512,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True)

    test_datagen = ImageDataGenerator(rescale=1./512)

    # 1st Parameter is the directory the training data is in.
    # 2nd Parameter is the expected size of the images.
    # 3rd is the batch size in which random samples of the given images will be included.
    # 4th Parameter states if your class is binary or has more then 2 categories.
    training_set = train_datagen.flow_from_directory(
            training_fpath,
            target_size=(512, 512),
            color_mode='grayscale',
            batch_size=16,
            shuffle=True,
            class_mode='binary')

    # Parameters represent the same thing as the Training_set does
    test_set = test_datagen.flow_from_directory(
            test_fpath,
            target_size=(512, 512),
            color_mode='grayscale',
            batch_size=1,
            shuffle=False,
            class_mode='binary')

    step_size_training = len(training_set)
    step_size_vaild = len(test_set)

    # 2nd parameter is the number of images that are in the original training set.
    # 3rd parameter is the number of epochs (How many generations) wanted to train the CNN.
    # 4th parameter is the set of images you want to test with.
    # 5th parameter is the number of test images.
    classifier.fit_generator(
        training_set,
        steps_per_epoch=step_size_training,
        epochs=1,
        validation_data=test_set,
        validation_steps=step_size_vaild)

    # Code below sets up stats on how the CNN did
    classifier.evaluate_generator(generator=test_set, steps=step_size_vaild)
    step_size_test = len(test_set)
    test_set.reset()
    percent_of_pred = classifier.predict_generator(test_set, steps=step_size_test, verbose=1)

    list_pred = []
    list_percent = []
    list_of_img_details = []

    percent_of_pred *= 100
    for x in percent_of_pred:
        # Pulls the predictions and adds it to a dictonary to be stored in a list.
        # Also gives the percent that it is certain it got it right.
        if x >= 50:
            list_percent.append(x)
            value = 'water'
        else:
            list_percent.append(x)
            value = 'no_water'

        list_pred.append(value)

    index = 0
    for file_name in os.listdir(test_fpath):
        # This loop creates a dictonary with all a images stats.
        for img_name in os.listdir(os.path.join(test_fpath, file_name)):
            details_of_img = {'img_name': '', 'status': '', 'prediction': '', 'percent': ''}
            details_of_img['img_name'] = img_name
            details_of_img['prediction'] = list_pred[index]
            details_of_img['percent'] = list_percent[index]
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
    img_names_list = img_functions.dictonary_pair_to_list('img_name', list_of_img_details)
    img_status = img_functions.dictonary_pair_to_list('status', list_of_img_details)
    results = pd.DataFrame({"Images": img_names_list, "Status": img_status,
                            "Predictions": list_pred,
                            "Percent": list_percent})
    CNN_STATS_FILE = img_functions.plot_img_incorrect_pred(list_of_img_details)
    img_functions.move_incorrect_predictions_back()

    results.to_csv(os.path.join(CNN_STATS_FILE, "results.csv"), index=True)

    # Saving the model
    classifier.save('asf_cnn.h5')
    classifier.save(os.path.join(CNN_STATS_FILE, 'asf_cnn.h5'))
    # Opens all the directory with all the stats so that the user can view them.
    os.system(f'xdg-open "{CNN_STATS_FILE}"')
