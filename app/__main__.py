"""Run the interactive calculator with python -m app."""

from colorama import Fore, Style, init

from app.calculator import Calculator
from app.exceptions import CalculatorError
from app.operations import OperationFactory


def show_help():
    """Display available operations and history commands."""
    print("\nEnter an operation followed by two numbers.")
    print("Example: add 2 3")
    print("\nOperations:")
    print(", ".join(OperationFactory.operations))
    print("\nOther commands:")
    print("history, clear, undo, redo, save, load, help, exit")
    print("For root, use: root NUMBER DEGREE")
    print("For percent, use: percent PART WHOLE")
    print()


def show_history(calculator):
    """Display recorded calculations."""
    if not calculator.history:
        print("History is empty.")
        return

    for index, record in enumerate(calculator.history, start=1):
        print(
            f"{index}. {record.operation}({record.a}, {record.b}) "
            f"= {record.result} [{record.timestamp}]"
        )


def handle_command(calculator, text):
    """Process one command; return False when the user exits."""
    parts = text.strip().split()

    if not parts:
        return True

    command = parts[0].lower()

    single_commands = {
        "history", "clear", "undo", "redo",
        "save", "load", "help", "exit",
    }

    if command in single_commands:
        if len(parts) != 1:
            raise CalculatorError(
                f"'{command}' does not accept additional arguments."
            )

        if command == "exit":
            return False

        if command == "help":
            show_help()
        elif command == "history":
            show_history(calculator)
        else:
            actions = {
                "clear": (calculator.clear, "History cleared."),
                "undo": (calculator.undo, "Undo completed."),
                "redo": (calculator.redo, "Redo completed."),
                "save": (calculator.save, "History saved."),
                "load": (calculator.load, "History loaded."),
            }
            action, message = actions[command]
            action()
            print(Fore.GREEN + message + Style.RESET_ALL)

        return True

    if command not in OperationFactory.operations:
        raise CalculatorError(
            f"Unknown command: {command}. Enter 'help' for commands."
        )

    if len(parts) != 3:
        raise CalculatorError(
            f"Usage: {command} NUMBER NUMBER"
        )

    record = calculator.calculate(command, parts[1], parts[2])
    print(Fore.GREEN + f"Result: {record.result}" + Style.RESET_ALL)
    return True


def main():
    """Start the read-eval-print loop and close resources on exit."""
    init(autoreset=True)

    try:
        calculator = Calculator()
    except (CalculatorError, OSError) as exc:
        print(Fore.RED + f"Startup error: {exc}" + Style.RESET_ALL)
        return 1

    try:
        print(Fore.CYAN + "Enhanced Calculator" + Style.RESET_ALL)
        show_help()

        while True:
            try:
                text = input("calculator> ")
                if not handle_command(calculator, text):
                    break
            except CalculatorError as exc:
                calculator.logger.warning("Command rejected: %s", exc)
                print(Fore.RED + f"Error: {exc}" + Style.RESET_ALL)
            except (EOFError, KeyboardInterrupt):
                print()
                break
    finally:
        calculator.close()

    print("Goodbye!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())