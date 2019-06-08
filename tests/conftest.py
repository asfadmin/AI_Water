import shutil
import tempfile

import pytest


@pytest.fixture
def tempdir():
    name = tempfile.mkdtemp(prefix='ai_water_tests_')
    yield name
    shutil.rmtree(name)
