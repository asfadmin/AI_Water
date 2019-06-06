# AI_Water
1) Run main.py, this will create all the need file directories.
2) Rename your dataset to dataset and extract it into AI_Project. labels.json
also needs to be placed to the AI_Project.
3) If you’re loading in weights rename the .h5 file to asf_cnn.h5 and move it to
the AI_Projects file. If you’re not loading them in and you're restarting the
training of the CNN, comment out the lines:

```python
with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
  classifier = load_model(os.path.join(CURRENT_DIRECTORY, 'AI_Project/asf_cnn.h5'))
```

And uncomment out the line:

```python
# classifier.compile('adam', loss='binary_crossentropy', metrics=['accuracy'])
```
4) Run main.py again.

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
