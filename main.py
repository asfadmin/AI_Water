"""
main.py can be ran in the terminal.
To run a test type:
    '$ python3 main.py test name_of_net name_of_dataset'
To train a a network tpye:
    '$ python3 main.py train awesome_net awesome_dataset --epochs 10'
For more information see README.md
"""

import os
from argparse import ArgumentParser, Namespace

from src.asf_cnn import test_model, train_model, test_masked_model
from src.dataset.common import dataset_type
from src.model import (
    create_model, load_model, model_type, path_from_model_name, ModelType
)
from src.plots import plot_confusion_chart, plot_predictions
from src.plots_masked import plot_predictions as plot_masked_predictions
from src.reports import write_dict_to_csv


def train_wrapper(args: Namespace) -> None:
    """Function for training a network"""
    data_type = dataset_type(args.dataset)
    model_name = args.model
    if args.cont:
        model = load_model(model_name)
        history = model.__asf_model_history
    else:
        model_path = path_from_model_name(model_name)
        if not args.overwrite and os.path.isfile(model_path):
            print(f"File {model_name} already exists!")
            return

        model = create_model(model_name, data_type)
        history = {"loss": [], "acc": [], "val_loss": [], "val_acc": []}

    if model_type(model) != data_type:
        print("ERROR: This dataset is not compatible with your model")
        return

    train_model(model, history, args.dataset, args.epochs)


def test_wrapper(args: Namespace) -> None:
    print(f'DELETE {dataset_type(args.dataset)} ***********************************' )
    model_name = args.model
    model = load_model(model_name)

    if model_type(model) != dataset_type(args.dataset):
        print("ERROR: This dataset is not compatible with your model")
        return
    if dataset_type(args.dataset) == ModelType.MASKED:
        print("Masked test_wrapper ***********************************************************")
        mask_pixel_preds = test_masked_model(model, args.dataset)
#        plot_masked_predictions(mask_pixel_preds, args.dataset)
    else:
        print('Binary test_wrapper ***********************************************************')
        details, confusion_matrix = test_model(model, args.dataset)

        model_dir = os.path.dirname(path_from_model_name(model_name))
        with open(os.path.join(model_dir, 'results.csv'), 'w') as f:
            write_dict_to_csv(details, f)

        plot_confusion_chart(confusion_matrix)
        plot_predictions(details['Percent'], args.dataset)


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
        print('DELETE ME *************************************')
        args.func(args)
    else:
        p.print_help()
