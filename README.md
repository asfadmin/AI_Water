# AI_Water ![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoidUtONGNXUzYvWDJod3V6MU9JMG95YlY3ZHUySXl2ZWtlQVd3V00xY3RwK3JMenFjM1ZuSHJpRzdEcjhKY1B5QmI0THZoTlI0ZGk4T0F0KzUydHVIRjVjPSIsIml2UGFyYW1ldGVyU3BlYyI6ImExM2llSGhpOE80OXhYczIiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)
Using Convolutional Neural Networks to generate water masks from SAR data.

## Installation

Installing dependencies is straight forward with pipenv. First install the
GDAL dev libraries:
```terminal
$ sudo apt-get install libgdal-dev
```

Then install the python packages:
```terminal
$ pipenv install --dev
```
Specifying the `--dev` flag will also install dependencies you will need to run
the training and unit tests.

NOTE: *If you have trouble installing PyGDAL make sure that the package version
in `Pipfile` corresponds to the version of your GDAL installation.*


To find GDALs package version run the following command:
```terminal
$ gdal-config --version
```

Next run this command:
```terminal
$ pip install gdal==(**YOUR VERSION***)
```

The last step is to run the following command in the terminal:
```terminal
$ pip install -e .
```

## Tiling .tiff Images
To tile your tiff image create a folder in the same directory as
main.py and name it prep_tiles. Store the tiff file within this
folder, like below:
```
AI_Water
├── prep_tiles
    └── name_of_img.tiff
```
Next run this command in the terminal (Note that 512 is the dimensions and
can be any arbitrary value, but to be ran in the provided Neural Network
it must be 512):


## Preparing Data With a Neural Network
To run the Neural Net your data will first need to be prepared.

Within the same directory that main.py resides create a new folder called 'datasets'.

Next, go to http://hyp3.asf.alaska.edu, click on the products tab, then finished.
Select the granules you'd like to use for your dataset. After that, click the
button that says "Download Python Script for Selected" and make sure it
downloads to the Downloads directory.

After that run make_data.py.

Command layout:
```terminal
$ python3 scripts/make_data.py ai_model_folder dataset_name dir_dataset_sits 512
```
Example:
```terminal
$ python scripts/make_data.py ai_model_7 Fairbanks Alaska 64
```
To get more information on preparing the data set run:
```terminal
$ python3 scripts/make_data.py prepare -h
```

After the program is finished the dataset is ready and the directory should
look like this:

```
AI_Water
└── datasets
    └── Alaska
        └── Fairbanks
            ├── test
            │   └── img1.vv.tif
            │   └── img1.vh.tif
            │   └── img1.mask.tif
            └── train
                └── img2.vv.tif
                └── img2.vh.tif
                └── img2.mask.tif
```

## Preparing data without a Network - Making Water Mask
To create a water mask download, you will need both a VV and VH granule.
Once you have them move them into a directory called prep_files (You might have
to create it). Next run this command:

```terminal
$ python scripts/identify_water.py prep_tiles/S1B_IW_RT30_20190924T145212_G_gpn_VV.tif  prep_tiles/S1B_IW_RT30_20190924T145212_G_gpn_VH.tif
```

Next, move the output 'mask-0.tif' into the directory prep_files.

## Preparing data without a Network - Tiling .tiff Images
To tile your tiff image create a folder in the same directory as
main.py and name it prep_tiles. Store the tiff file within this
folder, like below:
```
AI_Water
├── prep_tiles
    └── name_of_img.tiff
```
Next, run this command in the terminal (Note that 64 is the dimensions and
can be any arbitrary value, but to be ran in the provided Neural Network
it must be 64):

```terminal
$ python3 scripts/prepare_data.py tile tile_name_of_img.tiff 64
```

You will need to run this command for all the VV, VH, and Mask images.

To get more help on tiling run this
command:

```terminal
$ python3 scripts/prepare_data.py tile -h
```

## Project Layout
The project is organized into directories as follows.

```
AI_Water
├── datasets
│   └── example_rtc       # Each data set gets a directory
│       ├── test
│       └── train
├── models
│   └── example_net       # Each model gets a directory containing .h5 files
│       ├── epoch1.h5
│       ├── history.json
│       └── latest.h5
├── src                   # Neural network source code
├── tests                 # Unit and integration tests
│   ├── unit_tests
│   └── integration_tests
├── scripts               # Supporting script files
└── ...
```

## Running Unit Tests
This project uses `pytest` for unit testing. The easiest way to run the tests is
with pipenv. Make sure you have installed the development dependencies with:
```terminal
$ pipenv install --dev
```
Then you can run the tests and get the full report with:
```terminal
$ pipenv run tests
```

## Training
1. Make sure your dataset is in the `dataset` folder.
2. If you’re loading in weights run `main.py` with the `--continue` option.
If you’re not loading them in and you're restarting the training of the CNN you
will need to run `main.py` with the `--overwrite` option.

### Examples

Start training a new network:
```terminal
$ python3 main.py train awesome_net awesome_dataset --epochs 10
```

Evaluate the models performance:
```terminal
$ python3 main.py test awesome_net awesome_dataset
```

Train for an additional 20 epochs:
```terminal
$ python3 main.py train awesome_net awesome_dataset --epochs 20 --continue
```

## Getting Descriptive Information and Metrics
You can view information about a model's performance with `model_info.py`. This
includes a summary of model parameters, a visualization of convolutional
filters, a graph of training history and more.

View the models training history:
```terminal
$ python3 scripts/model_info.py awesome_net history
```

For a list of available statistics run the help command:
```terminal
$ python3 scripts/model_info.py -h
```
