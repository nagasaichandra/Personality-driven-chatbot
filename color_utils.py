#! /usr/bin/env python

# Source:
# https://github.com/RasaHQ/rasa/blob/a52ef66390abfdb445e7fa4f874435153ff960ad/rasa/cli/utils.py

import sys
from typing import Any, Text, NoReturn


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def wrap_with_color(*args: Any, color: Text):
    return color + " ".join(str(s) for s in args) + bcolors.ENDC


def print_color(*args: Any, color: Text):
    print(wrap_with_color(*args, color=color))


def bold(*args: Any):
    return wrap_with_color(*args, color=bcolors.BOLD)


def success(*args: Any):
    return wrap_with_color(*args, color=bcolors.OKGREEN + bcolors.BOLD)


def info(*args: Any):
    return wrap_with_color(*args, color=bcolors.OKCYAN + bcolors.BOLD)


def warning(*args: Any):
    return wrap_with_color(*args, color=bcolors.WARNING + bcolors.BOLD)


def error(*args: Any):
    return wrap_with_color(*args, color=bcolors.FAIL + bcolors.BOLD)


def print_success(*args: Any):
    print(success(*args))


def print_info(*args: Any):
    print(info(*args))


def print_warning(*args: Any):
    print(warning(*args))


def print_error(*args: Any):
    print(error(*args))


def print_error_and_exit(message: Text, exit_code: int = 1) -> NoReturn:
    """Print error message and exit the application."""

    print_error(message)
    sys.exit(exit_code)


def signal_handler(sig, frame) -> NoReturn:
    print("Goodbye 👋")
    sys.exit(0)
