"""Tests for saving and loading CSV history."""

import pandas as pd
import pytest

from app.calculation import Calculation
from app.exceptions import ValidationError
from app.history import HistoryManager


def test_save_and_load_history(tmp_path):
    manager = HistoryManager(tmp_path / "history" / "calculations.csv")
    records = [
        Calculation.create("add", 2, 3),
        Calculation.create("divide", 10, 4),
    ]

    manager.save(records)

    assert manager.load() == records


def test_save_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "history" / "calculations.csv"
    manager = HistoryManager(path)

    manager.save([])

    assert path.is_file()


def test_empty_history_round_trip(tmp_path):
    manager = HistoryManager(tmp_path / "empty.csv")

    manager.save([])

    assert manager.load() == []


def test_csv_has_required_columns(tmp_path):
    path = tmp_path / "calculations.csv"
    manager = HistoryManager(path)

    manager.save([Calculation.create("multiply", 3, 4)])

    dataframe = pd.read_csv(path)
    assert list(dataframe.columns) == HistoryManager.columns
    assert dataframe.iloc[0]["result"] == 12


def test_missing_history_file(tmp_path):
    manager = HistoryManager(tmp_path / "missing.csv")

    with pytest.raises(ValidationError, match="does not exist"):
        manager.load()


@pytest.mark.parametrize(
    "content",
    [
        "",
        "wrong,columns\n1,2\n",
        (
            "operation,a,b,result,timestamp\n"
            "add,hello,3,5,2026-10-25T12:00:00+00:00\n"
        ),
        (
            "operation,a,b,result,timestamp\n"
            "unknown,2,3,5,2026-10-25T12:00:00+00:00\n"
        ),
        (
            "operation,a,b,result,timestamp\n"
            "add,2,3,5,not-a-date\n"
        ),
    ],
)
def test_invalid_history_file(tmp_path, content):
    path = tmp_path / "invalid.csv"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValidationError):
        HistoryManager(path).load()


def test_save_failure(tmp_path, monkeypatch):
    manager = HistoryManager(tmp_path / "history.csv")

    def fail_to_save(*args, **kwargs):
        raise OSError("Disk unavailable")

    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_to_save)

    with pytest.raises(ValidationError, match="Could not save history"):
        manager.save([])


def test_load_failure(tmp_path, monkeypatch):
    manager = HistoryManager(tmp_path / "history.csv")

    def fail_to_read(*args, **kwargs):
        raise OSError("Cannot read file")

    monkeypatch.setattr(pd, "read_csv", fail_to_read)

    with pytest.raises(ValidationError, match="Could not load history"):
        manager.load()