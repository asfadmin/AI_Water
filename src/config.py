"""
 Created By:   ?
 Date Started: ?
 Last Updated: 07-13-2020
 File Name:    config.py
 Description:  Constants to be imported by other files.
"""

import re
from pathlib import Path
# credit to https://github.com/treigerm/WaterNet/blob/master/waterNet/config.py

# Current data directory structure
"""
data/
    -input/
        -products
        -aoi
    -working/
        -datasets
    -output/
        -models
        -mask
        -tensorboard
"""



# full Path to aiwater root
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Path configurations for data directory
DATA_DIR = PROJECT_DIR / "data"

# Input data subdirectory path configs
INPUT_DIR = DATA_DIR / "input"
PRODUCTS_DIR = INPUT_DIR / "products"
AOI_DIR = INPUT_DIR / "aoi"

# TODO: test directory?
# Working data subdirectory path configs
WORKING_DIR = DATA_DIR / "working"
DATASETS_DIR = WORKING_DIR / "datasets"

# Output data subdirectory path configs
OUTPUT_DIR = DATA_DIR / "output"
MODEL_DIR = OUTPUT_DIR / "models"
MASK_DIR = OUTPUT_DIR / "mask"
TENSORBOARD_DIR = OUTPUT_DIR / "tensorboard"

NETWORK_DEMS = 512

VH_REGEX = re.compile(r'(.*)_([0-9]+).vh.tif')
VV_REGEX = re.compile(r'(.*)_([0-9]+).vv.tif')
ZIP_REGEX = re.compile(r'S1(A|B)_IW(.*)-rtc-gamma\.zip')
BAND_REGEX = re.compile(r"(.*)(VV|VH|MASK)(.*)")
TYPE_REGEX = re.compile(r"(.*)_([0-9]+).(vv|vh|mask).(tiff|tif|TIFF|TIF)")
# For getting vv/vh from product directory
SAR_REGEX = re.compile(r"(S1[A|B])_(.{2})_(.*)_(VV|VH)(.tif)")