# AI_Water ![Build Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoidUtONGNXUzYvWDJod3V6MU9JMG95YlY3ZHUySXl2ZWtlQVd3V00xY3RwK3JMenFjM1ZuSHJpRzdEcjhKY1B5QmI0THZoTlI0ZGk4T0F0KzUydHVIRjVjPSIsIml2UGFyYW1ldGVyU3BlYyI6ImExM2llSGhpOE80OXhYczIiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)

Archived until a team picks back up this project.

Using Convolutional Neural Networks to generate water masks from SAR data.


# Installation

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


# scripts

All the scripts for the project can be found in aiwater.py. Make sure to run these scripts in a virtual enviroment.

## Setup

Run setup to create the file structure for working with the date.

```terminal
$ python aiwater.py setup
```

This will create the folling file structure:
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

These default directory's can be altered by modifying src/config.py.


## Download from metalink
ASF allows you to download product files from them using a .metalink file. You can choose the specific products to download from their site and then will be provided with a 'products.metalink' file.
```terminal
$ python aiwater.py download-metalink [metalink path] [output directory]
```


## Download from Hyp3 Subscription
You can download products directly from a hyp3 subscription to create your mask with. This functions allows you to limit your products to those which are of minimaly required to cover the given shape file. Also, you can also set a date bounds.

Date boudry option must be entered in format yyyy-mm-dd.

This script will require you to enter your earthdata credentials.


```terminal
$ python aiwater.py download-sub [name] --id [Subscription ID] --date-start [yyyy-mm-dd] --date-end [yyy-mm-dd] --aoi [Shape file path to area of interest] --min-cover [Sets mincover algorithm to true] --display [graphical shows final coverage] --output-dir [Ouput dir path]
```


## Create Mask

To create a single mask run:
```terminal
$ python aiwater.py create-mask [model name] [vv path] [vh path] [name]
```



## Mask a directory

Use this script to create a mask for every product in a directory:
```terminal
$ python aiwater.py mask-directory [model name] [source directory] [output directory] [mask name]
```


## Train the model

To train a new model run:
```terminal
$ python aiwater.py train [model name] [dataset name]
```

## Identify water via numeric method

```terminal
$ python aiwater.py identify-water [vv path] [vh path] [mask name]
```


## Tile an image


```terminal
$ python aiwater.py tile-image [image path] [tile size]
```

## Divide the dataset

Divide dataset into test and traid directories.

```terminal
$ python aiwater.py divide-dataset [directory] [test/train split (0.1-0.9)]
```

## Groom images

Groom images to remove inaccurate masks from the dataset.

```terminal
$ python aiwater.py groom-images [directory] [holdout]
```

## mask subscription

Basically runs download-sub and then mask-direcotry. Deletes directory when finished, leaving just the mask.

```terminal
$ python aiwater.py mask-sub [model name] [mask name]
```



## Project Layout
The project is organized into directories as follows.

```
AI_Water
├── aiwater.py            # Main Script with all comands
├── data
│   ├── input
│   │   ├── products      # unaltered product files
│   │   └── aoi           # AOI shape files
│   ├── working
│   │   └── datasets      # Tiled/groomed Datasets for training
│   └── output
│       ├── models      
│       └── mask        
├── src                   # source code
├── tests                 # Unit and integration tests
│   └── unit_tests
```

## Running Unit Tests
This project uses `pytest` for unit testing. The easiest way to run the tests is
with this make command:
```terminal
$ make test
```
