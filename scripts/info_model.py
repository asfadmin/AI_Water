import math
from argparse import ArgumentParser

from matplotlib import pyplot as plt
from tensorflow.keras.layers import Conv2D

from src.model import load_history, load_model


def print_summary_wrapper(args):
    print_summary(args.model)


def print_summary(model_name):
    model = load_model(model_name)
    model.summary()


def view_filters(model_name):
    model = load_model(model_name)
    for layer in model.layers:
        if not isinstance(layer, Conv2D):
            continue

        weights, biases = layer.get_weights()

        filter_width, filter_height, channels, num_filters = weights.shape

        nrows = math.ceil(math.sqrt(num_filters))
        ncols = math.ceil(num_filters / nrows)

        plt.figure(layer.name)
        plt.suptitle(f"Network layer: {layer.name}")
        x1w = weights[:, :, 0, :]
        for i in range(num_filters):
            plt.subplot(nrows, ncols, i + 1)
            plt.imshow(x1w[:, :, i], interpolation="nearest", cmap="gray")
    plt.show()


def view_filters_wrapper(args):
    view_filters(args.model)


def plot_history(model_name, history):
    plt.subplot(1, 2, 1)
    plt.plot(history['accuracy'])
    plt.plot(history['val_accuracy'])
    plt.title(f'{model_name} accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epochs')
    plt.legend(['Train', 'Test'], loc='lower right')

    plt.subplot(1, 2, 2)
    plt.plot(history['loss'])
    plt.plot(history['val_loss'])
    plt.title(f'{model_name} loss')
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.legend(['Train', 'Test'], loc='upper right')
    plt.show()


def plot_history_wrapper(args):
    plot_history(args.model, load_history(args.model))


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('model', help='Name of the saved model')

    sp = p.add_subparsers()

    summary = sp.add_parser('summary', help='View the keras model summary')
    summary.set_defaults(func=print_summary_wrapper)

    filters = sp.add_parser(
        'filters', help='Get a visual representation of filters for a model'
    )
    filters.set_defaults(func=view_filters_wrapper)

    hist = sp.add_parser(
        'history', help='View a plot of the model\'s training history'
    )
    hist.set_defaults(func=plot_history_wrapper)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
