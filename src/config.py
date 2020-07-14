"""
 Created By:   ?
 Date Started: ?
 Last Updated: 07-13-2020
 File Name:    config.py
 Description:  Constants to be imported by other files.
"""


import os
import re

PROJECT_DIR = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
DATASETS_DIR = os.path.join(PROJECT_DIR, 'datasets')
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
NETWORK_DEMS = 512

VH_REGEX = re.compile(r'(.*)_([0-9]+).vh.tif')
VV_REGEX = re.compile(r'(.*)_([0-9]+).vv.tif')


