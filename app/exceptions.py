"""Errors that the calculator can report to the user."""


class CalculatorError(Exception):
    """Base calculator error."""


class OperationError(CalculatorError):
    """An operation cannot be performed."""


class ValidationError(CalculatorError):
    """An input or setting is invalid."""
