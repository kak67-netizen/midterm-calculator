"""Store an immutable snapshot of calculation history."""

from dataclasses import dataclass

from app.calculation import Calculation


@dataclass(frozen=True)
class CalculatorMemento:
    """Preserve history so the calculator can restore it later."""

    history: tuple[Calculation, ...]

    @classmethod
    def capture(cls, history):
        """Copy the current history into an immutable snapshot."""
        return cls(history=tuple(history))

    def restore(self):
        """Return a fresh list containing the saved history."""
        return list(self.history)