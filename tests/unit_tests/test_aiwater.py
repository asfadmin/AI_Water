


import pytest

from argparse import Namespace
from aiwater import hello

def test_hello():
    input_namespace = Namespace(name='jason', count=3)
    input_str = hello(input_namespace)
    assert input_str=="hello jason!hello jason!hello jason!"

