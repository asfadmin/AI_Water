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
the unit tests.

NOTE: *If you have trouble installing PyGDAL make sure that the package version
in `Pipfile` corresponds to the version of your GDAL installation.*

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

```terminal
$ python3 tile_geotiff.py tile tile_name_of_img.tiff 512
```
To get more help on tiling run this
command:

```terminal
$ python3 tile_geotiff.py tile -h
```

## Classifying Images (for binary data sets)
In the terminal run the command:
```terminal
$ python3 tile_geotiff.py classify prep_tiles
```

to get more help run the command:
```terminal
$ python3 tile_geotiff.py classify -h
```

## Preparing Tiled and Classified Data Set
To run the Neural Net your data will first need to be prepared. This example
would have a binary output as it includes a labels.json file. A masked data set
would not have the labels.json file.

Within the same directory that main.py resides create a new folder called
'datasets'. Wrap all of your data and metadata into a folder and then move that
folder into data set. Below is an example of a tiled data set that is ready to
be restructured.

```
AI_Water
└── datasets
    └── example_rtc       # Each data set gets a directory
        ├── labels.json   # Your .json file needs to be named labels.json
        ├── img1.tif
        └── img2.tif
```

Once your data is in the correct directory run the following command:

```terminal
$ python3 tile_geotiff.py prepare datasets/example_rtc .3
```

This will move the image tiles into the directory structure expected by the
training script using a holdout of 30%.

To get more information on preparing the data set run:
```terminal
$ python3 tile_geotiff.py prepare -h
```

At this point your data set is ready and the directory should look like this:

```
AI_Water
└── datasets
    └── example_rtc
        ├── labels.json
        ├── test
        │   └── img1.tif
        └── train
            └── img2.tif
```

## Project Layout

The project is organized into directories as follows.

```
AI_Water
├── datasets
│   └── example_rtc       # Each data set gets a directory
│       ├── labels.json
│       ├── test
│       └── train
├── models
│   └── example_net       # Each model gets a directory containing .h5 files
│       ├── epoch1.h5
│       ├── history.json
│       └── latest.h5
├── src                   # Neural network source code
├── tests                 # Unit and integration tests
│   ├── unit_tests
│   └── integration_tests
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
1. Move your data set (along with `labels.json`) to the `dataset` folder.
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
$ python3 model_info.py awesome_net history
```

For a list of available statistics run the help command:
```terminal
$ python3 model_info.py -h
```
