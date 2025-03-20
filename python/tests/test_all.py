import pytest
import balance_engine


def test_sum_as_string():
    assert balance_engine.sum_as_string(1, 1) == "2"
