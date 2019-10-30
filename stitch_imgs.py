import re
from argparse import ArgumentParser
import os
from osgeo import gdal

PROJECTION = re.compile(r'AUTHORITY\["([A-Z]+)","([0-9]+)"\]')
MASK = re.compile(r'(.*)mask(.*)')

POWERS_OF_TWO = [128, 256, 512, 1024, 2048]


def check_power(pwr_of_two: int) -> bool:
    x = False
    for power in POWERS_OF_TWO:
        if pwr_of_two == power:

            x = True
            break
    return x


def build_up(path: str, pwr_of_two: int) -> None:
    """ This function takes a 64x64 input and allows the user to stitch
    the images into a larger one. The new size must be a power of 2
    larger than 64x64. """
    x = False
    while(True):  # Make sure user inputs a power of 2
        x = check_power(pwr_of_two)
        if x is False:
            print(f"{pwr_of_two} is not a power of two, try again: ")
            pwr_of_two = int(input())
            continue
        else:
            break

    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith('.tif'):
                continue
            try:
                tif = gdal.Open(os.path.join(root, file))
            except AttributeError:
                continue

            # Check to make sure the image isn't a full granule
            if tif.RasterXSize > 2048:
                continue


if __name__ == "__main__":
    # TODO: Remove after done with testing
    p = ArgumentParser()
    p.add_argument("path", help='path to the folder with imgs')
    # p.add_argument("power", help='Enter a power of two')

    args = p.parse_args()
    build_up(args.path, 63)
