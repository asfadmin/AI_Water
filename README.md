# AI_Water
Using Convolutional Neural Networks to generate water masks from SAR data.

## Installation

Installing dependencies is straight forward with pipenv. First install the
GDAL dev libraries:
```terminal
$ sudo apt-get install libgdal1-dev
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
To run the Neural Net your data will first need to be prepared.
(This example directory tree is a example of a binary output.
A masked output would not have the labels.json file)

Within the same directory that main.py resides create a new folder
called 'datasets'. Wrap all of your data and metadata into a folder
and then move that folder into data set. Below is an example of a
data set that is ready to be prepared for a binary output.

```
AI_Water
├── datasets
    └── example_rtc       # Each dataset gets a directory
        ├── labels.json   # Your .jsons file needs to be
        ├── img           # named labels.json
        ├── img
```

Once your data is in the correct spot move to the directory that
datasets resides. Next run this command:

```terminal
$ python3 tile_geotiff.py prepare datasets/example_rtc .3
```

The .3 at the end is the holdout, the proportion of data that
will be used for testing. At this point your data set is ready
and the file should look like this:

To get more information on preparing the data set run this
command:

```terminal
$ python3 tile_geotiff.py prepare -h
```

```
AI_Water
├── datasets
    └── example_rtc       # Each dataset gets a directory
        ├── labels.json
        ├── test
        └── train
```

## Project Layout

The project is organized into directories as follows.

```
AI_Water
├── datasets
│   └── example_rtc       # Each dataset gets a directory
│       ├── labels.json
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
1. Move your dataset (along with `labels.json`) to the dataset folder.
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

## Getting Information on a Model
Viewing information on a model is possible. The summary, filters,
and history of each model is saved to access the information later. 
To get access to this information use info_model.py, example:

View the models training history:
```terminal
$ python3 model_info.py awesome_net history
```

For help on running it type:
```terminal
$ python3 model_info.py -h
```
