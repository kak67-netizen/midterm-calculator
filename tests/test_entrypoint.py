"""Test launching the calculator as a Python module."""

import os
import subprocess
import sys


def test_module_entrypoint(tmp_path):
    environment = os.environ.copy()
    environment.update(
        {
            "CALCULATOR_LOG_DIR": str(tmp_path / "logs"),
            "CALCULATOR_HISTORY_DIR": str(tmp_path / "history"),
        }
    )

    result = subprocess.run(
        [sys.executable, "-m", "app"],
        input="exit\n",
        text=True,
        capture_output=True,
        env=environment,
        timeout=15,
    )

    assert result.returncode == 0
    assert "Enhanced Calculator" in result.stdout
    assert "Goodbye!" in result.stdout