"""Tests for calculation records."""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError


def test_create_calculation():
    record = Calculation.create(" ADD ", 2, 3)

    assert record.operation == "add"
    assert record.a == 2
    assert record.b == 3
    assert record.result == 5
    assert datetime.fromisoformat(record.timestamp)


def test_result_precision():
    record = Calculation.create("divide", 1, 3, precision=2)

    assert record.result == 0.33


def test_record_cannot_be_changed():
    record = Calculation.create("add", 2, 3)

    with pytest.raises(FrozenInstanceError):
        record.result = 99


def test_dictionary_round_trip():
    original = Calculation.create("multiply", 3, 4)

    restored = Calculation.from_dict(original.to_dict())

    assert restored == original


@pytest.mark.parametrize(
    "field,value",
    [
        ("a", "hello"),
        ("b", None),
        ("result", float("inf")),
        ("timestamp", "not-a-date"),
    ],
)
def test_invalid_record_values(field, value):
    data = Calculation.create("add", 2, 3).to_dict()
    data[field] = value

    with pytest.raises(ValidationError):
        Calculation.from_dict(data)


def test_missing_record_field():
    with pytest.raises(ValidationError):
        Calculation.from_dict({})


def test_unknown_record_operation():
    data = Calculation.create("add", 2, 3).to_dict()
    data["operation"] = "unknown"

    with pytest.raises(OperationError):
        Calculation.from_dict(data)