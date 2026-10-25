"""Tests for arithmetic results and invalid calculations."""

import pytest

from app.exceptions import OperationError
from app.operations import Add, OperationFactory


@pytest.mark.parametrize(
    "name,a,b,expected",
    [
        ("add", 2, 3, 5),
        ("add", -2, 3, 1),
        ("subtract", 2, 3, -1),
        ("multiply", -2, 3, -6),
        ("divide", 7, 2, 3.5),
        ("power", 2, 3, 8),
        ("power", 2, -2, 0.25),
        ("root", 27, 3, 3),
        ("root", -27, 3, -3),
        ("root", 16, -2, 0.25),
        ("modulus", 7, 3, 1),
        ("int_divide", 7, 2, 3),
        ("percent", 25, 200, 12.5),
        ("abs_diff", 2, 7, 5),
        ("abs_diff", 7, 2, 5),
    ],
)
def test_operation_results(name, a, b, expected):
    operation = OperationFactory.create(name)
    assert operation.execute(a, b) == pytest.approx(expected)


@pytest.mark.parametrize(
    "name,a,b",
    [
        ("divide", 1, 0),
        ("modulus", 1, 0),
        ("int_divide", 1, 0),
        ("percent", 1, 0),
        ("root", 9, 0),
        ("root", -16, 2),
        ("root", -16, 2.5),
        ("root", 0, -2),
        ("power", -1, 0.5),
        ("power", 0, -1),
        ("power", 1e308, 2),
        ("multiply", 1e308, 1e308),
    ],
)
def test_invalid_calculations(name, a, b):
    with pytest.raises(OperationError):
        OperationFactory.create(name).execute(a, b)


def test_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation"):
        OperationFactory.create("unknown")


def test_factory_normalizes_command():
    assert isinstance(OperationFactory.create(" ADD "), Add)


def test_factory_creates_separate_instances():
    assert OperationFactory.create("add") is not OperationFactory.create("add")
