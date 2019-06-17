"""
Tests to see if the output of the models architecture in masked_architecutre and binary_architecture
are correct.
"""
from src.model_architecture.binary_architecture import create_model_binary
from src.model_architecture.masked_architecture import create_model_masked


def model_final_layer(model):
    return str(model.layers[-1].output_shape)


def test_architecture():
    model = create_model_binary("binary_test")
    assert model_final_layer(model) == '(None, 1)'

    model = create_model_masked("masked_test")
    assert model_final_layer(model) == '(None, 512, 512, 1)'
