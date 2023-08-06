import pytest
from demo.Pytest_Que1 import Co_pyTest


def test_fun_positive():
    assert Co_pyTest(10, 2) == 12


def test_fun_negative():
    with pytest.raises(ValueError):
        Co_pyTest(10, -2)
