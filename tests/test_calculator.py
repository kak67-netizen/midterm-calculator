"""Tests for calculator behavior, history, and observers."""

from unittest.mock import Mock

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError


@pytest.fixture
def calculator(tmp_path, monkeypatch):
    """Create a calculator that saves only inside a temporary folder."""
    settings = {
        "CALCULATOR_LOG_DIR": str(tmp_path / "logs"),
        "CALCULATOR_HISTORY_DIR": str(tmp_path / "history"),
        "CALCULATOR_LOG_FILE": "calculator.log",
        "CALCULATOR_HISTORY_FILE": "calculations.csv",
        "CALCULATOR_MAX_HISTORY_SIZE": "3",
        "CALCULATOR_AUTO_SAVE": "true",
        "CALCULATOR_PRECISION": "4",
        "CALCULATOR_MAX_INPUT_VALUE": "1000",
        "CALCULATOR_DEFAULT_ENCODING": "utf-8",
    }
    for name, value in settings.items():
        monkeypatch.setenv(name, value)

    instance = Calculator(CalculatorConfig(env_file=None))
    yield instance
    instance.close()


def test_calculate_records_result(calculator):
    record = calculator.calculate("add", "2", "3")

    assert record.result == 5
    assert calculator.history == [record]


def test_calculate_uses_configured_precision(calculator):
    record = calculator.calculate("divide", 1, 3)

    assert record.result == 0.3333


@pytest.mark.parametrize(
    "operation,a,b,error",
    [
        ("add", "hello", 2, ValidationError),
        ("add", 1001, 2, ValidationError),
        ("divide", 1, 0, OperationError),
        ("unknown", 1, 2, OperationError),
    ],
)
def test_invalid_calculation_preserves_history(
    calculator, operation, a, b, error
):
    original = calculator.calculate("add", 2, 3)

    with pytest.raises(error):
        calculator.calculate(operation, a, b)

    assert calculator.history == [original]


def test_history_size_limit(calculator):
    for number in range(5):
        calculator.calculate("add", number, 1)

    assert len(calculator.history) == 3
    assert [record.result for record in calculator.history] == [3, 4, 5]


def test_undo_and_redo(calculator):
    first = calculator.calculate("add", 2, 3)
    second = calculator.calculate("multiply", 3, 4)

    calculator.undo()
    assert calculator.history == [first]

    calculator.redo()
    assert calculator.history == [first, second]


@pytest.mark.parametrize("command", ["undo", "redo"])
def test_empty_undo_or_redo(calculator, command):
    with pytest.raises(ValidationError, match="Nothing to"):
        getattr(calculator, command)()


def test_new_calculation_clears_redo(calculator):
    calculator.calculate("add", 1, 2)
    calculator.undo()
    calculator.calculate("multiply", 3, 4)

    with pytest.raises(ValidationError, match="Nothing to redo"):
        calculator.redo()


def test_invalid_calculation_preserves_redo(calculator):
    record = calculator.calculate("add", 1, 2)
    calculator.undo()

    with pytest.raises(OperationError):
        calculator.calculate("divide", 1, 0)

    calculator.redo()
    assert calculator.history == [record]


def test_clear_can_be_undone(calculator):
    record = calculator.calculate("add", 2, 3)

    calculator.clear()
    assert calculator.history == []

    calculator.undo()
    assert calculator.history == [record]


def test_manual_save_and_load(calculator):
    record = calculator.calculate("add", 2, 3)
    calculator.save()
    calculator.history.clear()

    calculator.load()

    assert calculator.history == [record]


def test_load_can_be_undone(calculator):
    first = calculator.calculate("add", 1, 2)
    second = calculator.calculate("multiply", 3, 4)

    # Make the saved history different from the current history.
    calculator.history_manager.save([first])

    calculator.load()
    assert calculator.history == [first]

    calculator.undo()
    assert calculator.history == [first, second]


def test_load_respects_history_limit(calculator):
    records = [
        calculator.calculate("add", number, 1)
        for number in range(5)
    ]
    calculator.history_manager.save(records)

    calculator.load()

    assert calculator.history == records[-3:]


def test_auto_save_tracks_changes(calculator):
    record = calculator.calculate("add", 2, 3)
    assert calculator.history_manager.load() == [record]

    calculator.undo()
    assert calculator.history_manager.load() == []

    calculator.redo()
    assert calculator.history_manager.load() == [record]

    calculator.clear()
    assert calculator.history_manager.load() == []


def test_observer_registered_once(calculator):
    observer = Mock()

    calculator.register_observer(observer)
    calculator.register_observer(observer)
    record = calculator.calculate("add", 2, 3)

    observer.update.assert_called_once_with(record, [record])


def test_observer_failure_preserves_calculation(calculator, capsys):
    observer = Mock()
    observer.update.side_effect = OSError("Disk unavailable")
    calculator.register_observer(observer)

    record = calculator.calculate("add", 2, 3)

    assert calculator.history == [record]
    assert "Warning:" in capsys.readouterr().out
    assert "Observer failed" in calculator.config.log_file.read_text()


def test_auto_save_failure_reports_warning(calculator, monkeypatch, capsys):
    calculator.calculate("add", 2, 3)
    failing_save = Mock(side_effect=ValidationError("Disk unavailable"))
    monkeypatch.setattr(calculator.history_manager, "save", failing_save)

    calculator.undo()

    assert calculator.history == []
    assert "Warning:" in capsys.readouterr().out
    assert "Auto-save failed" in calculator.config.log_file.read_text()


def test_manual_save_failure(calculator, monkeypatch):
    failing_save = Mock(side_effect=ValidationError("Disk unavailable"))
    monkeypatch.setattr(calculator.history_manager, "save", failing_save)

    with pytest.raises(ValidationError, match="Disk unavailable"):
        calculator.save()

    assert "Manual save failed" in calculator.config.log_file.read_text()


def test_load_failure_preserves_history(calculator, monkeypatch):
    record = calculator.calculate("add", 2, 3)
    failing_load = Mock(side_effect=ValidationError("Invalid file"))
    monkeypatch.setattr(calculator.history_manager, "load", failing_load)

    with pytest.raises(ValidationError, match="Invalid file"):
        calculator.load()

    assert calculator.history == [record]
    assert "History load failed" in calculator.config.log_file.read_text()


def test_auto_save_disabled(calculator):
    config = calculator.config
    config.auto_save = False
    instance = Calculator(config)

    try:
        assert len(instance.observers) == 1
        instance.calculate("add", 2, 3)
        instance.undo()
        assert not config.history_file.exists()

        instance.save()
        assert config.history_file.exists()
    finally:
        instance.close()