"""Coordinate calculations, history, observers, and undo/redo."""

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import CalculatorError, ValidationError
from app.history import HistoryManager
from app.input_validators import validate_number
from app.logger import AutoSaveObserver, Logger, LoggingObserver


class Calculator:
    """Manage calculator state and notify registered observers."""

    def __init__(self, config=None):
        self.config = config if config is not None else CalculatorConfig()
        self.history = []
        self._undo_stack = []
        self._redo_stack = []
        self.observers = []

        self.history_manager = HistoryManager(
            self.config.history_file,
            self.config.encoding,
        )
        self.logger = Logger(
            self.config.log_file,
            self.config.encoding,
        )

        self.register_observer(LoggingObserver(self.logger))

        if self.config.auto_save:
            self.register_observer(
                AutoSaveObserver(self.history_manager)
            )

        self.logger.info("Calculator started")

    def register_observer(self, observer):
        """Register an observer once."""
        if observer not in self.observers:
            self.observers.append(observer)

    def _remember(self):
        """Save the current state before making a new change."""
        self._undo_stack.append(
            CalculatorMemento.capture(self.history)
        )
        self._redo_stack.clear()

    def calculate(self, operation, a, b):
        """Validate inputs, calculate, and record the result."""
        try:
            first = validate_number(a, self.config.max_input_value)
            second = validate_number(b, self.config.max_input_value)
            record = Calculation.create(
                operation,
                first,
                second,
                self.config.precision,
            )
        except CalculatorError as exc:
            self.logger.warning("Calculation rejected: %s", exc)
            raise

        self._remember()
        self.history.append(record)
        self.history = self.history[-self.config.max_history_size:]

        for observer in self.observers:
            try:
                observer.update(record, list(self.history))
            except Exception as exc:
                # A storage failure must not erase a valid calculation.
                self.logger.error("Observer failed: %s", exc)
                print(f"Warning: calculation completed, but {exc}")

        return record

    def _save_after_change(self):
        """Keep the saved history consistent when auto-save is enabled."""
        if self.config.auto_save:
            try:
                self.history_manager.save(self.history)
            except CalculatorError as exc:
                self.logger.error("Auto-save failed: %s", exc)
                print(f"Warning: history changed, but {exc}")

    def undo(self):
        """Restore the state before the most recent change."""
        if not self._undo_stack:
            raise ValidationError("Nothing to undo.")

        self._redo_stack.append(
            CalculatorMemento.capture(self.history)
        )
        self.history = self._undo_stack.pop().restore()
        self.logger.info("History change undone")
        self._save_after_change()

    def redo(self):
        """Restore the most recently undone state."""
        if not self._redo_stack:
            raise ValidationError("Nothing to redo.")

        self._undo_stack.append(
            CalculatorMemento.capture(self.history)
        )
        self.history = self._redo_stack.pop().restore()
        self.logger.info("History change redone")
        self._save_after_change()

    def clear(self):
        """Clear history while allowing the action to be undone."""
        self._remember()
        self.history.clear()
        self.logger.info("History cleared")
        self._save_after_change()

    def save(self):
        """Save the current history manually."""
        try:
            self.history_manager.save(self.history)
        except CalculatorError as exc:
            self.logger.error("Manual save failed: %s", exc)
            raise

        self.logger.info("History saved")

    def load(self):
        """Load history without changing current state if reading fails."""
        try:
            loaded = self.history_manager.load()
        except CalculatorError as exc:
            self.logger.error("History load failed: %s", exc)
            raise

        self._remember()
        self.history = loaded[-self.config.max_history_size:]
        self.logger.info("History loaded")

    def close(self):
        """Release logging resources."""
        self.logger.info("Calculator closed")
        self.logger.close()