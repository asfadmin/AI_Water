"""
Alaska Satellite Facility
Convolutional Neural Network
McKade Sorensen (Douglas)
05/21/2019

main.py, runs the code for AI_Project. The first time the program runs it'll create the files
needed. After its ran once the dataset folder (with all the SAR images) needs to be extracted into
AI_Project. asf_cnn.h5 and labels.json both need to be moved there into the AI_Project folder.
"""

import csv
import os
from argparse import ArgumentParser

from matplotlib import pyplot
# import asf_cnn as cnn
# import img_functions
from src.asf_cnn import test_model, train_model
from src.model import create_model, load_model, path_from_model_name


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

    if args.cont:
        model = load_model(model_name)
        history = model.__asf_model_history
    else:
        model_path = path_from_model_name(model_name)
        if not args.overwrite and os.path.isfile(model_path):
            print(f"File {model_name} already exists!")
            return
        model = create_model(model_name)
        history = {"loss": [], "acc": [], "val_loss": [], "val_acc": []}

    train_model(model, history, args.dataset, args.epochs)


def test_wrapper(args):
    model_name = args.model
    model = load_model(model_name)

    details, confusion_matrix = test_model(model, args.dataset)

    # TODO: Refactor this to an analytics module
    model_path = path_from_model_name(model_name)
    with open(
        os.path.join(os.path.dirname(model_path), 'results.csv'), 'w'
    ) as f:
        writer = csv.writer(f)

        rows = []
        for header, values in details.items():
            if not rows:
                rows.append([header])
                for value in values:
                    rows.append([value])
            else:
                rows[0].append(header)
                for i, value in enumerate(values):
                    rows[i + 1].append(value)

        writer.writerows(rows)

    width, height = confusion_matrix.shape
    for x in range(width):
        for y in range(height):
            pyplot.annotate(
                str(confusion_matrix[x][y]),
                xy=(y, x),
                horizontalalignment='center',
                verticalalignment='center'
            )

    pyplot.imshow(confusion_matrix, cmap=pyplot.get_cmap('RdBu'))
    pyplot.xlabel("Actual")
    pyplot.ylabel("Predicted")
    pyplot.xticks(range(width))
    pyplot.yticks(range(height))
    pyplot.colorbar()
    pyplot.show()


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
