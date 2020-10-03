"""
 Created By:   ?
 Date Started: ?
 Last Updated: 07-13-2020
 File Name:    config.py
 Description:  Constants to be imported by other files.
"""

import os
import re

# credit to https://github.com/treigerm/WaterNet/blob/master/waterNet/config.py

from pathlib import Path

# full Path to aiwater root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Path configurations for data directory
DATA_DIR = PROJECT_ROOT / "data"

# Input data subdirectory path configs
INPUT_DIR = DATA_DIR / "input"
SENTINEL_DIR = INPUT_DIR / "sentinel1"
SHAPEFILE_DIR = INPUT_DIR / "shape_files"

# TODO: test directory?
# Working data subdirectory path configs
WORKING_DIR = DATA_DIR / "working"
MODEL_WEIGHTS_DIR = WORKING_DIR / "models"
TRAIN_DIR = WORKING_DIR / "training_data"
TILES_DIR = TRAIN_DIR / "tiles"
WATER_MASKS_DIR = TRAIN_DIR / "water_masks"
LABELS_DIR = TRAIN_DIR / "labels_images"

# Output data subdirectory path configs
OUTPUT_DIR = DATA_DIR / "output"
TENSORBOARD_DIR = OUTPUT_DIR / "tensorboard"

PROJECT_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
DATASETS_DIR = os.path.join(PROJECT_DIR, 'datasets')
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
NETWORK_DEMS = 512

VH_REGEX = re.compile(r'(.*)_([0-9]+).vh.tif')
VV_REGEX = re.compile(r'(.*)_([0-9]+).vv.tif')
ZIP_REGEX = re.compile(r'S1(A|B)_IW(.*)-rtc-gamma\.zip')
BAND_REGEX = re.compile(r"(.*)(VV|VH|MASK)(.*)")
TYPE_REGEX = re.compile(r"(.*)_([0-9]+).(vv|vh|mask).(tiff|tif|TIFF|TIF)")
