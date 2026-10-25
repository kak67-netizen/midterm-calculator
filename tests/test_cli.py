"""Tests for the interactive command-line interface."""

from unittest.mock import Mock

import pytest

import app.__main__ as cli
from app.calculation import Calculation
from app.exceptions import CalculatorError


@pytest.fixture
def calculator():
    instance = Mock()
    instance.history = []
    return instance


def test_help_lists_operations(capsys):
    cli.show_help()

    output = capsys.readouterr().out
    assert "add" in output
    assert "root" in output
    assert "undo" in output
    assert "exit" in output


def test_empty_history(calculator, capsys):
    cli.show_history(calculator)

    assert "History is empty." in capsys.readouterr().out


def test_display_history(calculator, capsys):
    calculator.history = [Calculation.create("add", 2, 3)]

    cli.show_history(calculator)

    assert "add(2, 3) = 5" in capsys.readouterr().out


@pytest.mark.parametrize("text", ["", "   "])
def test_blank_command(calculator, text):
    assert cli.handle_command(calculator, text) is True


def test_exit_command(calculator):
    assert cli.handle_command(calculator, "EXIT") is False


@pytest.mark.parametrize("command", ["help", "history"])
def test_display_commands(calculator, command, capsys):
    assert cli.handle_command(calculator, command) is True
    assert capsys.readouterr().out


@pytest.mark.parametrize("command", ["clear", "undo", "redo", "save", "load"])
def test_history_commands(calculator, command):
    assert cli.handle_command(calculator, command) is True
    getattr(calculator, command).assert_called_once_with()


def test_calculation_command(calculator, capsys):
    calculator.calculate.return_value = Calculation.create("add", 2, 3)

    assert cli.handle_command(calculator, "ADD 2 3") is True

    calculator.calculate.assert_called_once_with("add", "2", "3")
    assert "Result: 5" in capsys.readouterr().out


@pytest.mark.parametrize(
    "text",
    ["help extra", "exit extra", "unknown", "add", "add 1", "add 1 2 3"],
)
def test_invalid_commands(calculator, text):
    with pytest.raises(CalculatorError):
        cli.handle_command(calculator, text)


def test_main_recovers_from_error(calculator, monkeypatch, capsys):
    monkeypatch.setattr(cli, "Calculator", lambda: calculator)
    commands = iter(["unknown", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(commands))

    assert cli.main() == 0

    output = capsys.readouterr().out
    assert "Error: Unknown command" in output
    assert "Goodbye!" in output
    calculator.logger.warning.assert_called_once()
    calculator.close.assert_called_once()


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_main_handles_interruption(calculator, monkeypatch, error):
    monkeypatch.setattr(cli, "Calculator", lambda: calculator)

    def interrupted_input(prompt):
        raise error()

    monkeypatch.setattr("builtins.input", interrupted_input)

    assert cli.main() == 0
    calculator.close.assert_called_once()


@pytest.mark.parametrize(
    "error",
    [CalculatorError("Invalid configuration"), OSError("Cannot open log")],
)
def test_startup_error(monkeypatch, capsys, error):
    def failed_startup():
        raise error

    monkeypatch.setattr(cli, "Calculator", failed_startup)

    assert cli.main() == 1
    assert "Startup error:" in capsys.readouterr().out