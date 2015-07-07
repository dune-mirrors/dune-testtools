import pytest


@pytest.fixture
def dir():
    import os
    return os.path.dirname(os.path.abspath(__file__)) + "/"
