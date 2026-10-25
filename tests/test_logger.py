"""Tests for file logging and calculation observers."""

from unittest.mock import Mock

from app.calculation import Calculation
from app.logger import AutoSaveObserver, Logger, LoggingObserver


def test_logger_writes_all_levels(tmp_path):
    path = tmp_path / "logs" / "calculator.log"
    logger = Logger(path)

    try:
        logger.info("Calculator started")
        logger.warning("Invalid input: %s", "hello")
        logger.error("Calculation failed")
    finally:
        logger.close()

    content = path.read_text(encoding="utf-8")

    assert "INFO Calculator started" in content
    assert "WARNING Invalid input: hello" in content
    assert "ERROR Calculation failed" in content


def test_logger_releases_handlers(tmp_path):
    logger = Logger(tmp_path / "calculator.log")

    logger.close()

    assert logger.logger.handlers == []


def test_logging_observer_records_calculation(tmp_path):
    path = tmp_path / "calculator.log"
    logger = Logger(path)
    record = Calculation.create("add", 2, 3)

    try:
        observer = LoggingObserver(logger)
        observer.update(record, [record])
    finally:
        logger.close()

    content = path.read_text(encoding="utf-8")

    assert "Calculation: add(2, 3) = 5" in content


def test_auto_save_observer_saves_history():
    manager = Mock()
    record = Calculation.create("multiply", 3, 4)
    history = [record]
    observer = AutoSaveObserver(manager)

    observer.update(record, history)

    manager.save.assert_called_once_with(history)


def test_separate_loggers_do_not_duplicate_messages(tmp_path):
    path = tmp_path / "calculator.log"
    first = Logger(path)
    second = Logger(path)

    try:
        first.info("First event")
        second.info("Second event")
    finally:
        first.close()
        second.close()

    content = path.read_text(encoding="utf-8")

    assert content.count("First event") == 1
    assert content.count("Second event") == 1