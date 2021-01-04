# AI_Water ![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoidUtONGNXUzYvWDJod3V6MU9JMG95YlY3ZHUySXl2ZWtlQVd3V00xY3RwK3JMenFjM1ZuSHJpRzdEcjhKY1B5QmI0THZoTlI0ZGk4T0F0KzUydHVIRjVjPSIsIml2UGFyYW1ldGVyU3BlYyI6ImExM2llSGhpOE80OXhYczIiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)
Using Convolutional Neural Networks to generate water masks from SAR data.

## Table of Content 

- [Installation](#installation)
    - [Fixing Gdal](#Installing-Gdal)
- [Preparing Data](#Preparing-Data)
    - [Tile images](#Tiling-tif-Images)
    - [Preparing Data With a Neural Network](#Preparing-Data-With-a-Neural-Network)
    - [Preparing Data Without a Neural Network](#Preparing-data-without-Neural-a-Network)
- [Project layout](#Project-Layout)
- [Running Unit Tests](#Running-Unit-Tests)
- [Training a Neural Network](#Training-a-Neural-Network)
    - [Examples](#Examples)
    - [Getting Descriptive Information and Metrics](#Getting-Descriptive-Information-and-Metrics)

## Requirements
- python3.8
- GDAL



## GDAL

First install the
GDAL dev libraries:
```terminal
$ sudo apt install libgdal-dev
```


## Pipenv
We are using pipenv to track dependicies instead of a requirements.txt file.
So `pipenv` will have to be installed.
```terminal
$ pip3 install pipenv
```

Then create a new virtual environment inside of the AI_Water directory.

```terminal
$ virtualenv .venv --python=python3.8
```


Then enter the new virtual environment:
```terminal
$ pipenv shell
```


Install the python packages from the pipfile:
```terminal
$ pipenv install --dev
```
Specifying the `--dev` flag will also install dependencies you will need to run
the training and unit tests.

Finally run setup.py:
```terminal
$ pip3 install -e .
```



## Installing pygdal

GDAL can take some troubleshooting to get working properly in a virtual environment.
This is why we use the pygdal wrapper.

NOTE: *pygdal must have the same version as GDAL to work!*

To find GDALs package version run the following command:
```terminal
$ gdal-config --version
```

Next run this command, inputing your version of GDAL:
```terminal
$ pip3 install pygdal==<Your GDAL version>
```

or you can also try this:
```terminal
$ pip3 install pygdal=="`gdal-config --version`.*"
```




## Docker

To run the container version with proper volume mounting run the make command:
```terminal
$ make container
```

There can sometimes be issues getting the GUI to output from the container.
To test this run the following while in the container:
NOTE: *Outputing gui via container is expiremental. It may not work as expected.*
```terminal
$ apt-get install x11-apps -y; xeyes
```
You should see the following:

![xeyes screnshot](xeyes.png?raw=true "xeyes")

If you do not see xeyes (the googly eyes) then any script with a GUI will most likely not work.
run the following command on the host machine (not in the container),
and then try running xeyes again.
```terminal
$ xhost +
```

### Tiling tif Images
To tile your tif image you can use this command:
```terminal
$ python aiwater.py tile-image image_path tile_size
```
This will tile the image in the same directory as the image.

## Preparing Data
To run the Neural Net, your data will first need to be prepared. There are a few methods of creating data but all of 
them require a `datasets` directory within `AI_Water`.  

If the `datasets` directory wasn't created during `setup.py`, cd into the directory `AI_Water` and then run the command:
```terminal
$ mkdir datasets
```
Datasets should be a folder containing train and tests directories. You can create these by placing tiled images in a folder and 
running this command:
```terminal
$ python aiwater.py divide-dataset directory_path holdout
```

## Making Water Mask without Neural Network

First follow the instructions in the [Preparing Data](#Preparing-Data) section.
`identify-water` can be used to an approximate water mask, given dual band SAR images (VV and VH). This is done without a Neural Network.
Simply drag the filter bar down to make the detection less sensitive until the results are close. There is also the option to draw a polygon
around misidentified water to remove it by clicking around the area. 

```terminal
$ python aiwater.py identify-water vv_image_path vh_image_path
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
with this make command:
```terminal
$ make test
```

## Training a Neural Network
1. Make sure your dataset is in the `dataset` folder.
2. If you’re loading in weights run `python aiwater.py train --continue ...`
If you’re not loading them in and you're restarting the training of the CNN you
will need to run `python aiwater.py --overwrite ...`

### Examples

Start training a new network:
```terminal
$ python3 aiwater.py train awesome_net awesome_dataset --epochs 10
```

Evaluate the models performance:
```terminal
$ python3 aiwater.py test awesome_net awesome_dataset
```

Train for an additional 20 epochs:
```terminal
$ python3 aiwater.py train awesome_net awesome_dataset --epochs 20 --continue
```

NOTE: *`awesome_net` and `awesome_dataset` must be in a directories named `models` and `datasets` that live in `AI_Water`.*

## Creating a Mask with the Neural Network
First, you'll need the VV and VH images. Then enter this command:
```terminal
$ python3 aiwater.py create-mask model_path vv_image_path vh_image_path mask_name.tif
```

## Getting Descriptive Information and Metrics
You can view information about a model's performance with `model_info.py`. This
includes a summary of model parameters, a visualization of convolutional
filters, a graph of training history and more.

To view this information use these commands:
```terminal
$ python3 aiwater.py model-history awesome_net
$ python3 aiwater.py model-summary awesome_net
$ python3 aiwater.py model-filters awesome_net
```
NOTE: *`awesome_net` must be in a directory named `models` that lives in `AI_Water`.*


