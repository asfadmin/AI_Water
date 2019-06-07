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

NOTE: *If you have trouble installing GDAL make sure that the package version
in `Pipfile` corresponds to your GDAL installation.*

## Training
1. Move your dataset (along with `labels.json`) to the dataset folder.
2. If you’re loading in weights run `main.py` with the `--continue` option.
If you’re not loading them in and you're restarting the training of the CNN you
will need to run `main.py` with the `--overwrite` option.

### Examples

Start training a new network:
```terminal
$ python main.py train awesome_net awesome_dataset --epochs 10
```

Evaluate the models performance:
```terminal
$ python main.py test awesome_net awesome_dataset
```

Train for an additional 20 epochs:
```terminal
$ python main.py train awesome_net awesome_dataset --epochs 20 --continue
```

View the models training history:
```terminal
$ python model_info.py awesome_net history
```


## Project Layout

The project is organized into directories as follows.

```
AI_Water
├── dataset
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
