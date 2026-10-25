"""Configure calculator logging and observe new calculations."""

import logging
from pathlib import Path
from uuid import uuid4


class Logger:
    """Write calculator events to a log file."""

    def __init__(self, file_path, encoding="utf-8"):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(
            f"calculator.{uuid4().hex}"
        )
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        handler = logging.FileHandler(path, encoding=encoding)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s"
            )
        )
        self.logger.addHandler(handler)

    def info(self, message, *args):
        self.logger.info(message, *args)

    def warning(self, message, *args):
        self.logger.warning(message, *args)

    def error(self, message, *args):
        self.logger.error(message, *args)

    def close(self):
        """Release file handlers when the application exits."""
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)


class LoggingObserver:
    """Log each new calculation when the calculator notifies us."""

    def __init__(self, logger):
        self.logger = logger

    def update(self, calculation, history):
        self.logger.info(
            "Calculation: %s(%s, %s) = %s",
            calculation.operation,
            calculation.a,
            calculation.b,
            calculation.result,
        )


class AutoSaveObserver:
    """Save history when the calculator reports a new calculation."""

    def __init__(self, history_manager):
        self.history_manager = history_manager

    def update(self, calculation, history):
        self.history_manager.save(history)