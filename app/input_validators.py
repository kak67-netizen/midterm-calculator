"""Validate numerical inputs before performing calculations."""

import math

from app.exceptions import ValidationError


def validate_number(value, max_input_value):
    """Return a finite number within the configured input limit."""
    if isinstance(value, bool):
        raise ValidationError("Enter a number, not a Boolean value.")

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError("Enter a valid number.") from exc

    if not math.isfinite(number):
        raise ValidationError("Number must be finite.")

    if abs(number) > max_input_value:
        raise ValidationError(
            f"Number must be between {-max_input_value:g} "
            f"and {max_input_value:g}."
        )

    return number