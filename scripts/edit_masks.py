"""
 McKade Sorensen
 11-11-19
 edit_mask.py
"""
import re
from argparse import ArgumentParser
import os
from src.plots import edit_predictions
from src.asf_cnn import test_model_masked
from src.model import load_model
from src.prepare_64_data import break_up_images


def remove_64(path: str) -> None:
    REGEX = re.compile(r"(.*)_([0-9]+).(.*).x([0-9]+)_y([0-9]+).tif")
    for root, dirs, files in os.walk(path):
        for file in files:

            m = re.match(REGEX, file)
            if not m or not file.endswith('.tif'):
                continue
            os.remove(os.path.join(root, file))


def run_gui(path: str, model) -> None:
    predictions, data_iter, metadata = test_model_masked(
        model, path, True, dems=512
    )
    edit_predictions(
        predictions, data_iter, metadata, dem=512
    )


def main(path: str) -> None:
    full_path = os.path.join("datasets", path)
    model = load_model("ai_test_7")
    remove_64(full_path)
    run_gui(path, model)
    print("Finishing up...")
    break_up_images(full_path)


if __name__ == "__main__":
    # TODO: Remove after done with testing
    p = ArgumentParser()
    p.add_argument("path", help='path to the folder with imgs')
    # p.add_argument("power", help='Enter a power of two')

    args = p.parse_args()
    main(args.path)
