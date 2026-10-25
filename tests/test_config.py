"""Tests for configuration defaults, files, and invalid settings."""

import os
from pathlib import Path

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Keep tests independent of existing calculator settings."""
    for name in list(os.environ):
        if name.startswith("CALCULATOR_"):
            monkeypatch.delenv(name)


def test_default_settings():
    config = CalculatorConfig(env_file=None)

    assert config.log_dir == Path("logs")
    assert config.history_dir == Path("history")
    assert config.log_file == Path("logs/calculator.log")
    assert config.history_file == Path("history/calculations.csv")
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 4
    assert config.max_input_value == 1000000000
    assert config.encoding == "utf-8"


def test_load_settings_from_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CALCULATOR_PRECISION=2\n"
        "CALCULATOR_AUTO_SAVE=false\n"
        "CALCULATOR_MAX_HISTORY_SIZE=25\n"
        "CALCULATOR_MAX_INPUT_VALUE=500\n"
        "CALCULATOR_LOG_DIR=custom_logs\n"
        "CALCULATOR_HISTORY_DIR=custom_history\n"
        "CALCULATOR_LOG_FILE=custom.log\n"
        "CALCULATOR_HISTORY_FILE=custom.csv\n"
        "CALCULATOR_DEFAULT_ENCODING=ascii\n",
        encoding="utf-8",
    )

    # load_dotenv changes the environment; restore it after this test.
    original_environment = os.environ.copy()
    try:
        config = CalculatorConfig(env_file=env_file)
    finally:
        os.environ.clear()
        os.environ.update(original_environment)

    assert config.precision == 2
    assert config.auto_save is False
    assert config.max_history_size == 25
    assert config.max_input_value == 500
    assert config.log_file == Path("custom_logs/custom.log")
    assert config.history_file == Path("custom_history/custom.csv")
    assert config.encoding == "ascii"


def test_environment_overrides_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CALCULATOR_PRECISION=2\n", encoding="utf-8")
    monkeypatch.setenv("CALCULATOR_PRECISION", "6")

    config = CalculatorConfig(env_file=env_file)

    assert config.precision == 6


@pytest.mark.parametrize(
    "name,value",
    [
        ("CALCULATOR_MAX_HISTORY_SIZE", "0"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "abc"),
        ("CALCULATOR_PRECISION", "-1"),
        ("CALCULATOR_PRECISION", "16"),
        ("CALCULATOR_PRECISION", "2.5"),
        ("CALCULATOR_AUTO_SAVE", "yes"),
        ("CALCULATOR_MAX_INPUT_VALUE", "abc"),
        ("CALCULATOR_MAX_INPUT_VALUE", "0"),
        ("CALCULATOR_MAX_INPUT_VALUE", "-10"),
        ("CALCULATOR_MAX_INPUT_VALUE", "inf"),
        ("CALCULATOR_MAX_INPUT_VALUE", "nan"),
        ("CALCULATOR_DEFAULT_ENCODING", "not-an-encoding"),
    ],
)
def test_invalid_settings(monkeypatch, name, value):
    monkeypatch.setenv(name, value)

    with pytest.raises(ValidationError):
        CalculatorConfig(env_file=None)