"""Save and load calculation history using pandas."""

from pathlib import Path

import pandas as pd

from app.calculation import Calculation
from app.exceptions import OperationError, ValidationError


class HistoryManager:
    """Manage CSV storage for calculation records."""

    columns = ["operation", "a", "b", "result", "timestamp"]

    def __init__(self, file_path, encoding="utf-8"):
        self.file_path = Path(file_path)
        self.encoding = encoding

    def save(self, history):
        """Save history, including column headings for empty history."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            records = [record.to_dict() for record in history]
            dataframe = pd.DataFrame(records, columns=self.columns)
            dataframe.to_csv(
                self.file_path,
                index=False,
                encoding=self.encoding,
            )
        except (OSError, UnicodeError, ValueError) as exc:
            raise ValidationError(
                f"Could not save history: {exc}"
            ) from exc

    def load(self):
        """Load valid records or report a helpful file error."""
        try:
            dataframe = pd.read_csv(
                self.file_path,
                encoding=self.encoding,
                keep_default_na=False,
            )

            if list(dataframe.columns) != self.columns:
                raise ValidationError(
                    "History CSV must contain these columns in order: "
                    + ", ".join(self.columns)
                )

            return [
                Calculation.from_dict(row)
                for row in dataframe.to_dict(orient="records")
            ]
        except FileNotFoundError as exc:
            raise ValidationError(
                "History file does not exist. Save history first."
            ) from exc
        except (
            OSError,
            UnicodeError,
            ValueError,
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
            OperationError,
        ) as exc:
            raise ValidationError(
                f"Could not load history: {exc}"
            ) from exc