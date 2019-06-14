"""
masked_architecture_test.py is used to test if the data is being
loaded properly when creating a model
"""
import unittest

from src.model_architecture.masked_architecture import create_model_masked


class TestMaskedArchitecture(unittest.TestCase):

    def test_model(self):
        """Test to see if the model returns the correct output"""
        model = create_model_masked('masked_test')
        model_final_layer = str(model.layers[-1].output_shape)
        self.assertEqual(model_final_layer, '(None, 512, 512, 1)')


if __name__ == '__main__':
    unittest.main()
