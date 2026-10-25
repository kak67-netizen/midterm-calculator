"""Represent a completed calculation."""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.exceptions import ValidationError
from app.operations import OperationFactory


@dataclass(frozen=True)
class Calculation:
    """An immutable record of a completed calculation."""

    operation: str
    a: float
    b: float
    result: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def create(cls, operation, a, b, precision=4):
        """Perform an operation and create its history record."""
        name = operation.strip().lower()
        result = OperationFactory.create(name).execute(a, b)

        return cls(
            operation=name,
            a=a,
            b=b,
            result=round(result, precision),
        )

    def to_dict(self):
        """Convert the record into a row for CSV storage."""
        return {
            "operation": self.operation,
            "a": self.a,
            "b": self.b,
            "result": self.result,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data):
        """Restore a record from a CSV row."""
        try:
            operation = str(data["operation"]).strip().lower()
            OperationFactory.create(operation)

            numbers = [
                float(data[name]) for name in ("a", "b", "result")
            ]
            if not all(math.isfinite(number) for number in numbers):
                raise ValueError("Values must be finite.")

            timestamp = str(data["timestamp"])
            datetime.fromisoformat(timestamp)

            return cls(operation, *numbers, timestamp=timestamp)
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise ValidationError(
                "History contains an invalid calculation record."
            ) from exc