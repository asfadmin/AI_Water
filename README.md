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
    - [Examples](*Examples)
    - [Getting Descriptive Information and Metrics](#Getting-Descriptive-Information-and-Metrics)
- [Scripts](#Scripts)
    - [Identify Water](#Identify-Water)
    - [Info Model](#Info-Model)
    - [Mask Subscriptions](#Mask-Subscription)
    - [Create Mask](#Create-Mask)
    - [Make Data](#Make-Data)
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

The last step is to run the following command in the terminal:
```terminal
$ pip install -e .
```

### Installing Gdal
NOTE: *If you have trouble installing PyGDAL make sure that the package version
in `Pipfile` corresponds to the version of your GDAL installation, or run the commands below.*


To find GDALs package version run the following command:
```terminal
$ gdal-config --version
```

Next run this command:
```terminal
$ pip install gdal==(**YOUR VERSION***)
```

If an error appears try running the following command:
```terminal
$ pip install pygdal==(**YOUR VERSION***)
```

### Tiling tif Images
To tile your tif image create a folder in the same directory as
main.py and name it prep_tiles. Store the tif file within this
folder, like below:
```
AI_Water
├── prep_tiles
    └── name_of_img.tiff
```
Next run this command in the terminal (Note that 512 is the dimensions and
can be any arbitrary value, but to be ran in the provided Neural Network
it must be 512):

## Preparing Data
To run the Neural Net, your data will first need to be prepared. There are a few methods of creating data but all of 
them require a `datasets` directory within `AI_Water`.  

Once in the directory `AI_Water` run the command:
```terminal
$ python3 mkdir datasets

```

### Preparing Data With a Neural Network

After following instructions in the [Preparing Data](#Preparing-Data) section, go to http://hyp3.asf.alaska.edu, click on the products tab, then finished.
Select the granules you'd like to use for your dataset. After that, click the
button that says "Download Python Script for Selected" and make sure it
downloads to the Downloads directory.

After that run make_data.py.

Command layout:
```terminal
$ python3 scripts/make_data.py ai_model_folder dataset_name dir_dataset_sits 512

```
NOTE: *`ai_model_folder` and `dataset_name` must be in a directories named `models` and `datasets` that live in `AI_Water`.*

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

### Preparing data without a Neural Network 
**Making Water Mask:**

First follow the instructions in the [Preparing Data](#Preparing-Data) section.

To create a water mask download, you will need both a VV and VH granule.
Once you have them move them into a directory called prep_files (You might have
to create it). Next run this command:

```terminal
$ python scripts/identify_water.py prep_tiles/S1B_IW_RT30_20190924T145212_G_gpn_VV.tif  prep_tiles/S1B_IW_RT30_20190924T145212_G_gpn_VH.tif
```

Next, move the output 'mask-0.tif' into the directory prep_files.

**Tiling:**

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

## Training a Neural Network
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

NOTE: *`awesome_net` and `awesome_dataset` must be in a directories named `models` and `datasets` that live in `AI_Water`.*

## Getting Descriptive Information and Metrics
You can view information about a model's performance with `model_info.py`. This
includes a summary of model parameters, a visualization of convolutional
filters, a graph of training history and more.

View the models training history:
```terminal
$ python3 scripts/model_info.py awesome_net history
```

NOTE: *`awesome_net` must be in a directory named `models` that lives in `AI_Water`.*

For a list of available statistics run the help command:
```terminal
$ python3 scripts/model_info.py -h
```

## Scripts
Scripts contained within `AI_Water`.

### Identify Water
`identify_water.py` can be used to an approximate water mask, given dual band SAR images (VV and VH). This is done without a Neural Network.

Example command:
 ```terminal
$ python3 scripts/identify_water.py full_path_to_vv_img full_path_to_vh_img

```
### Info Model
`info_model.py` is explained under the section [Getting Descriptive Information and Metrics](#Getting-Descriptive-Information-and-Metrics).

### Mask Subscription
`mask_subscription.py` can be used to mask a users subscription from [ASF HYP3](http://hyp3.asf.alaska.edu).
The output is a list of water masks created from the granules within the subscription, and a vrt.

Example command:
 ```terminal
$ python3 scripts/identify_water.py ai_model_folder name_of_vrt_output

```

After the program is ran, you will be asked for your [Nasa Earthdata](https://earthdata.nasa.gov) Credentials.
```
Enter your NASA EarthData username: 
Password: 
```
If one were able to login in successfully and have subscriptions through [ASF HYP3](http://hyp3.asf.alaska.edu), one
should see similar text as  below:

```
login successful!
Welcome user
ID: 1949: Arizona
ID: 1893: Washington
ID: 1959: Lake_Erie
ID: 1836: UAF
ID: 1826: Alaska
Pick an id from the list above: 
```
The final step is to pick an ID that is listed. Inputting 1826 will create a mask from the subscription `Alaska`.

### Create Mask
`create_mask.py` can be used to create a water mask using a Neural Network, given dual band SAR images (VV and VH).
Example command:
 ```terminal
$ python3 scripts/create_mask.py ai_model_folder full_path_to_vv_img full_path_to_vh_img output_mask_name

```

### Make Data
`make_data.py` is explained under the section [Preparing Data With a Neural Network](#Preparing-Data-With-a-Neural-Network).
