"""Arithmetic operations and their factory."""

import math
from abc import ABC, abstractmethod

from app.exceptions import OperationError


class Operation(ABC):
    """Common interface for all arithmetic operations."""

    def execute(self, a, b):
        """Calculate a finite real result or raise a helpful error."""
        try:
            result = self.calculate(a, b)
            if isinstance(result, complex) or not math.isfinite(result):
                raise OperationError("Result must be a finite real number.")
            return result
        except (ZeroDivisionError, OverflowError, ValueError) as exc:
            raise OperationError(f"Cannot perform calculation: {exc}") from exc

    @abstractmethod
    def calculate(self, a, b):
        """Calculate using two numerical inputs."""


class Add(Operation):
    def calculate(self, a, b):
        return a + b


class Subtract(Operation):
    def calculate(self, a, b):
        return a - b


class Multiply(Operation):
    def calculate(self, a, b):
        return a * b


class Divide(Operation):
    def calculate(self, a, b):
        return a / b


class Power(Operation):
    def calculate(self, a, b):
        return a ** b


class Root(Operation):
    def calculate(self, a, b):
        if b == 0:
            raise OperationError("Root degree cannot be zero.")
        if a < 0:
            if not float(b).is_integer() or int(b) % 2 == 0:
                raise OperationError(
                    "A negative number requires an odd integer root degree."
                )
            return -((-a) ** (1 / b))
        return a ** (1 / b)


class Modulus(Operation):
    def calculate(self, a, b):
        return a % b


class IntegerDivide(Operation):
    def calculate(self, a, b):
        return a // b


class Percentage(Operation):
    def calculate(self, a, b):
        return (a / b) * 100


class AbsoluteDifference(Operation):
    def calculate(self, a, b):
        return abs(a - b)


class OperationFactory:
    """Create an operation instance from its command name."""

    operations = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntegerDivide,
        "percent": Percentage,
        "abs_diff": AbsoluteDifference,
    }

    @classmethod
    def create(cls, name):
        try:
            operation_class = cls.operations[name.strip().lower()]
        except KeyError as exc:
            raise OperationError(f"Unknown operation: {name}") from exc
        return operation_class()
