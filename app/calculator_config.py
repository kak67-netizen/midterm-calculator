"""Load and validate calculator settings."""

import codecs
import math
import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ValidationError


class CalculatorConfig:
    """Read settings from environment variables and a .env file."""

    def __init__(self, env_file=".env"):
        if env_file is not None:
            load_dotenv(env_file, override=False)

        self.log_dir = Path(
            os.getenv("CALCULATOR_LOG_DIR", "logs")
        )
        self.history_dir = Path(
            os.getenv("CALCULATOR_HISTORY_DIR", "history")
        )

        self.log_file = self.log_dir / os.getenv(
            "CALCULATOR_LOG_FILE", "calculator.log"
        )
        self.history_file = self.history_dir / os.getenv(
            "CALCULATOR_HISTORY_FILE", "calculations.csv"
        )

        self.max_history_size = self._read_integer(
            "CALCULATOR_MAX_HISTORY_SIZE", 100, minimum=1
        )
        self.precision = self._read_integer(
            "CALCULATOR_PRECISION", 4, minimum=0, maximum=15
        )

        auto_save = os.getenv(
            "CALCULATOR_AUTO_SAVE", "true"
        ).strip().lower()

        if auto_save not in {"true", "false"}:
            raise ValidationError(
                "CALCULATOR_AUTO_SAVE must be true or false."
            )

        self.auto_save = auto_save == "true"

        try:
            self.max_input_value = float(
                os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1000000000")
            )
        except ValueError as exc:
            raise ValidationError(
                "CALCULATOR_MAX_INPUT_VALUE must be a number."
            ) from exc

        if (
            not math.isfinite(self.max_input_value)
            or self.max_input_value <= 0
        ):
            raise ValidationError(
                "CALCULATOR_MAX_INPUT_VALUE must be finite and positive."
            )

        self.encoding = os.getenv(
            "CALCULATOR_DEFAULT_ENCODING", "utf-8"
        )

        try:
            codecs.lookup(self.encoding)
        except LookupError as exc:
            raise ValidationError(
                "CALCULATOR_DEFAULT_ENCODING must be a valid encoding."
            ) from exc

    @staticmethod
    def _read_integer(name, default, minimum, maximum=None):
        """Read a whole-number setting and check its allowed range."""
        try:
            value = int(os.getenv(name, str(default)))
        except ValueError as exc:
            raise ValidationError(
                f"{name} must be a whole number."
            ) from exc

        if value < minimum:
            raise ValidationError(
                f"{name} must be at least {minimum}."
            )

        if maximum is not None and value > maximum:
            raise ValidationError(
                f"{name} must be no greater than {maximum}."
            )

        return value