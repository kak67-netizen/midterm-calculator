"""Tests for numerical input validation."""

import pytest

from app.exceptions import ValidationError
from app.input_validators import validate_number


@pytest.mark.parametrize(
    "value,expected",
    [
        ("12", 12),
        ("-3.5", -3.5),
        (" 2.5 ", 2.5),
        ("1e2", 100),
        (0, 0),
        (1000, 1000),
        (-1000, -1000),
    ],
)
def test_valid_numbers(value, expected):
    assert validate_number(value, 1000) == expected


@pytest.mark.parametrize(
    "value",
    [
        "hello",
        "",
        None,
        True,
        False,
        "nan",
        "inf",
        "-inf",
        1001,
        -1001,
        [],
        10 ** 1000,
    ],
)
def test_invalid_numbers(value):
    with pytest.raises(ValidationError):
        validate_number(value, 1000)