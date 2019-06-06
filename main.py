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
from argparse import ArgumentParser

# import asf_cnn as cnn
# import img_functions
from src.asf_cnn import train_model
from src.model import create_model, kload_model, path_from_model_name


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


def train_wrapper(args):
    model_name = args.model
    model_path = path_from_model_name(model_name)
    if not args.overwrite and os.path.isfile(model_path):
        print(f"File {model_name} already exists!")
        return

    if args.cont:
        model = kload_model(model_path)
    else:
        model = create_model()

    train_model(model, args.dataset, args.epochs)


def test_wrapper(args):
    test_model(args.model, args.dataset)


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    # Arguments for train mode
    train = sp.add_parser('train', help='Train a new model')
    train.add_argument('model', help='Name of the model to save: example_net')
    train.add_argument('dataset', nargs='?', default='dataset_calibrated')
    train.add_argument(
        '--overwrite',
        '-o',
        action='store_true',
        help='Replace the file if it exists'
    )
    train.add_argument(
        '--continue',
        '-c',
        action='store_true',
        dest='cont',
        help='Continue training from existing model'
    )
    train.add_argument('--epochs', '-e', type=int, default=10)
    train.set_defaults(func=train_wrapper)

    # Arguments for test mode
    test = sp.add_parser('test', help='Test an existing model')
    test.add_argument('model', help='Name of the trained model')
    test.add_argument('dataset', nargs='?', default='dataset_calibrated')
    test.set_defaults(func=test_wrapper)

    # Parse and execute selected function
    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
