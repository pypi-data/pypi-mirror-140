"""Unit testing a module function."""
from lifespline_utils.example import example
from conftest import test_cases, arg_example

def test_example(test_cases):
    """All the test cases will pass."""
    res = True

    for test_case in test_cases:
        inp = test_case[0]
        exp_out = test_case[1]
        res = res and (example(inp) == exp_out)

    assert res

def test_arg_example(arg_example):
    assert arg_example