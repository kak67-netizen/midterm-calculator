# Enhanced Calculator Command-Line Application

A Python calculator with arithmetic operations, undo/redo, CSV history,
configurable settings, logging, and automated tests.

## Features

- Ten arithmetic operations.
- Interactive command-line interface.
- Input validation and helpful error messages.
- Undo and redo for history changes.
- CSV history saving and loading using pandas.
- Automatic history saving and calculation logging.
- Configuration through environment variables and a .env file.
- Colored results, confirmations, and error messages using Colorama.
- GitHub Actions enforcing a minimum test coverage of 90%.

## Requirements

- Python 3.12 or later.
- Git.
- WSL or another environment supporting the commands below.

## Installation

Clone the repository and enter its folder:

```bash
git clone https://github.com/kak67-netizen/midterm-calculator.git
cd midterm-calculator
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create your local configuration:

```bash
cp .env.example .env
```

## Configuration

Edit `.env` to customize the application.

| Setting | Default | Purpose |
|---|---|---|
| CALCULATOR_LOG_DIR | logs | Directory containing log files |
| CALCULATOR_HISTORY_DIR | history | Directory containing CSV history |
| CALCULATOR_LOG_FILE | calculator.log | Log filename within the log directory |
| CALCULATOR_HISTORY_FILE | calculations.csv | CSV filename within the history directory |
| CALCULATOR_MAX_HISTORY_SIZE | 100 | Maximum number of current history records |
| CALCULATOR_AUTO_SAVE | true | Automatically save history after changes |
| CALCULATOR_PRECISION | 4 | Decimal places used to round results |
| CALCULATOR_MAX_INPUT_VALUE | 1000000000 | Maximum absolute value of either input |
| CALCULATOR_DEFAULT_ENCODING | utf-8 | Encoding used for log and CSV files |

Existing environment variables take priority over values in `.env`.
Missing settings use defaults.

History size must be a positive integer. Precision must be an integer
from 0 through 15. Auto-save must be `true` or `false`. The input limit
must be finite and positive, and the encoding must be recognized.

The `.env` file is excluded from Git. The `.env.example` file provides
sample settings.

Restart the application after changing settings.

## Running the Calculator

From the project root, with the virtual environment active:

```bash
python -m app
```

Enter commands at the `calculator>` prompt.

### Arithmetic Commands

Each arithmetic command takes exactly two numerical inputs.

| Command | Example | Result |
|---|---|---|
| add | add 2 3 | 5 |
| subtract | subtract 8 3 | 5 |
| multiply | multiply 4 3 | 12 |
| divide | divide 10 4 | 2.5 |
| power | power 2 3 | 8 |
| root | root 27 3 | 3 |
| modulus | modulus 7 3 | 1 |
| int_divide | int_divide 7 2 | 3 |
| percent | percent 25 200 | 12.5 |
| abs_diff | abs_diff 2 7 | 5 |

For root, the first input is the number and the second is the root
degree. Negative numbers require an odd integer root degree.
The degree cannot be zero.

Percentage uses `(a / b) * 100`.

Integer division discards the fractional part toward zero.
For example, `int_divide -7 2` returns `-3`.

Calculations use Python floating-point numbers, with results rounded
to the configured precision.

### History and Application Commands

| Command | Purpose |
|---|---|
| history | Display current calculation history |
| clear | Clear history; this action can be undone |
| undo | Restore history before the previous change |
| redo | Restore the most recently undone history state |
| save | Save current history to CSV |
| load | Load history from CSV; this action can be undone |
| help | Display available commands |
| exit | Close the application |

Undo and redo operate during the current session. A successful new
calculation, clear, or load action clears the redo stack.

The application starts with empty history. Use `load` to restore a
previously saved CSV before performing new calculations. With auto-save
enabled, a new calculation replaces the CSV with the current session's
history.

CSV files contain `operation`, `a`, `b`, `result`, and `timestamp` columns.
Application-generated timestamps use UTC.

When auto-save is enabled, calculations, clear, undo, and redo save
the current history automatically. The load command reads the existing
file without immediately rewriting it.

### Example Session

```text
calculator> add 2 3
Result: 5.0
calculator> divide 10 4
Result: 2.5
calculator> undo
Undo completed.
calculator> redo
Redo completed.
calculator> save
History saved.
calculator> exit
Goodbye!
```

## Error Handling and Logging

The calculator rejects nonnumeric inputs, nonfinite values, inputs
outside the configured limit, and invalid calculations such as division
by zero.

Custom exceptions distinguish validation errors from operation errors.
The command-line interface displays helpful messages and allows the
user to try again.

Missing or malformed history files produce helpful errors. A failed
load preserves the current history.

Logs are written to `logs/calculator.log` by default:

- INFO records startup, calculations, history actions, and shutdown.
- WARNING records rejected calculations and commands.
- ERROR records observer and history storage failures.

If automatic saving fails, the completed calculation remains in memory
and the application displays a warning.

## Design Patterns

### Factory

`OperationFactory` creates an arithmetic operation instance from its
command name. Each operation implements the common `Operation`
interface.

### Memento

`CalculatorMemento` stores immutable history snapshots used by undo
and redo. Restoring a snapshot returns a separate history list.

### Observer

The calculator notifies registered observers after a new calculation.
`LoggingObserver` records the calculation. `AutoSaveObserver` saves the
current history when automatic saving is enabled.

## Project Structure

```text
app/
    __init__.py
    __main__.py
    calculation.py
    calculator.py
    calculator_config.py
    calculator_memento.py
    exceptions.py
    history.py
    input_validators.py
    logger.py
    operations.py
tests/
    __init__.py
    test_calculation.py
    test_calculator.py
    test_cli.py
    test_config.py
    test_entrypoint.py
    test_history.py
    test_input_validators.py
    test_logger.py
    test_memento.py
    test_operations.py
.github/
    workflows/
        python-app.yml
.coveragerc
.env.example
.gitignore
README.md
requirements.txt
```

Runtime log and history directories are created as needed and excluded
from Git. The virtual environment and generated coverage data are also
excluded.

## Testing

Run all tests:

```bash
python -m pytest -v
```

Run tests with coverage and enforce the required minimum:

```bash
python -m pytest --cov=app --cov-config=.coveragerc --cov-report=term-missing --cov-fail-under=90
```

The current test suite contains 149 passing tests and achieves 100%
statement coverage, including launching the application as a Python
module.

Tests cover arithmetic, configuration, input validation, calculation
records, CSV persistence, snapshots, logging, observers, calculator
behavior, and the command-line interface.

Parameterized tests cover multiple inputs, including negative numbers,
division by zero, invalid root degrees, and invalid configuration values.

The `.coveragerc` file enables coverage measurement in subprocesses so
the application launch test contributes to the coverage report.

File tests use temporary directories to protect actual application data.

## Continuous Integration

GitHub Actions installs dependencies and runs the tests on every push
and on pull requests targeting `main`. The workflow can also be started
manually from the Actions tab.

The workflow fails if a test fails or total coverage is below 90%.
Coverage configuration is read automatically from `.coveragerc`.

## Additional Feature

Colorama provides green results and confirmations, red errors, and a
cyan application heading.