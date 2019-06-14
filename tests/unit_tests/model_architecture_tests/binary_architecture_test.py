"""
binary_architecture_test.py is used to test if the data is being
loaded properly when creating a model
"""
import unittest

from src.model_architecture.binary_architecture import create_model_binary


class TestBinaryArchitecture(unittest.TestCase):

    def test_model(self):
        """Test to see if the model returns binary output"""
        model = create_model_binary("binary_test")
        model_final_layer = str(model.layers[-1].output_shape)
        self.assertEqual(model_final_layer, '(None, 1)')


if __name__ == '__main__':
    unittest.main()
