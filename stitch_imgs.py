import re
from argparse import ArgumentParser
import os


def remove_64(path: str):
    REGEX = re.compile(r"(.*)_([0-9]+).(.*).x([0-9]+)_y([0-9]+).tif")
    for root, dirs, files in os.walk(path):
        for file in files:

            m = re.match(REGEX, file)
            if not m or not file.endswith('.tif'):
                continue
            os.remove(os.path.join(root, file))


if __name__ == "__main__":
    # TODO: Remove after done with testing
    p = ArgumentParser()
    p.add_argument("path", help='path to the folder with imgs')
    # p.add_argument("power", help='Enter a power of two')

    args = p.parse_args()
    remove_64(args.path)
