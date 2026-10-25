"""Tests for history snapshots."""

from dataclasses import FrozenInstanceError

import pytest

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def test_capture_empty_history():
    snapshot = CalculatorMemento.capture([])

    assert snapshot.history == ()
    assert snapshot.restore() == []


def test_capture_preserves_records():
    record = Calculation.create("add", 2, 3)
    snapshot = CalculatorMemento.capture([record])

    assert snapshot.restore() == [record]


def test_changing_original_list_does_not_change_snapshot():
    record = Calculation.create("add", 2, 3)
    history = [record]
    snapshot = CalculatorMemento.capture(history)

    history.clear()

    assert snapshot.restore() == [record]


def test_changing_restored_list_does_not_change_snapshot():
    record = Calculation.create("multiply", 3, 4)
    snapshot = CalculatorMemento.capture([record])

    restored = snapshot.restore()
    restored.clear()

    assert snapshot.restore() == [record]


def test_each_restore_returns_a_separate_list():
    snapshot = CalculatorMemento.capture([])

    assert snapshot.restore() is not snapshot.restore()


def test_snapshot_cannot_be_changed():
    snapshot = CalculatorMemento.capture([])

    with pytest.raises(FrozenInstanceError):
        snapshot.history = ()