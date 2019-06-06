import os

from keras.preprocessing.image import ImageDataGenerator

from .config import PROJECT_DIR


def load_dataset(dataset: str):
    # File paths for grabbing the images.
    training_fpath = os.path.join(PROJECT_DIR, 'dataset', dataset, 'train')
    test_fpath = os.path.join(PROJECT_DIR, 'dataset', dataset, 'test')
    print(PROJECT_DIR)

    # Part 2: Fitting the CNN to the image
    # Implementing data augmentation, creates more images from given images.
    train_datagen = ImageDataGenerator(
        rescale=1. / 512, shear_range=0.2, zoom_range=0.2, horizontal_flip=True
    )

    test_datagen = ImageDataGenerator(rescale=1. / 512)

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
        class_mode='binary'
    )

    # Parameters represent the same thing as the Training_set does
    test_set = test_datagen.flow_from_directory(
        test_fpath,
        target_size=(512, 512),
        color_mode='grayscale',
        batch_size=1,
        shuffle=False,
        class_mode='binary'
    )

    return training_set, test_set
