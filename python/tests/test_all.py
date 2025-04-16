import pytest
import engine


def test_sum_as_string():
    assert engine.sum_as_string(1, 1) == "2"
