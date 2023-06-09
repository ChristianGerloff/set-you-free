import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional

# TODO: decide which methods here are needed in the refactoring?


def get_numeric_month_by_string(string: str, fallback_month: Optional[str] = "01") -> str:
    """Get a numeric month representation given a month string representation.

    Args:
        string (str): Month string representation (e.g., jan, january, Jan, Feb, December).
        fallback_month (Optional[str], optional): Month string representation to be returned on any error.
            Defaults to "01".

    Returns:
        str: A month numeric representation (e.g. jan -> 01).
    """
    months = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    if string and isinstance(string, str):
        if string.isdigit() and 1 <= int(string) <= 12:
            return f"{int(string):02d}"
        elif string[:3].lower() in months:
            return f"{months[string[:3].lower()]:02d}"

    return fallback_month


def try_success(
    function: Callable,
    attempts: Optional[int] = 1,
    pre_delay: Optional[int] = 0,
    next_try_delay: Optional[int] = 3,
) -> Callable | None:
    """Tries to execute a function and repeat the execution if it raises any exception.
    This function will try N times to succeed, by provided number of attempts.

    Args:
        function (Callable): A function that will be tried N times.
        attempts (Optional[int], optional): Number of attempts. Defaults to 1.
        pre_delay (Optional[int], optional): The delay before each function attempts in seconds. Defaults to 0.
        next_try_delay (Optional[int], optional): The delay between function attempts in seconds. Defaults to 3.

    Returns:
        Callable | None: Returns the returned value of function or None if function raises Exception in all attempts.
    """
    try:
        if attempts > 0:
            time.sleep(pre_delay)
            return function()
        else:
            return None
    except Exception as e:
        logging.debug(e, exc_info=True)
        time.sleep(next_try_delay)
        return try_success(function, attempts - 1)


def clear() -> None:  # pragma: no cover
    """Clear the console."""
    if os.name in ("nt", "dos"):
        subprocess.call("cls")
    elif os.name in ("linux", "osx", "posix"):
        subprocess.call("clear")
    else:
        print("\n") * 120


def check_write_access(path: str) -> None:
    """Check if you can write on the provided path or not.

    Args:
        path (str): A OS path

    Raises:
        PermissionError: If you can't write on the provided path
    """
    try:
        with Path(path).open("a"):
            pass
    except Exception:
        raise PermissionError("You can't write on the provided path")


def logging_initialize(verbose: Optional[bool] = False) -> None:
    """Initializes logging method. If verbose mode is True then logging will be initialized on DEBUG mode.
    Otherwise, INFO mode will be used.

    Args:
        verbose (Optional[bool], optional): If the logging needs to be verbose.
            Defaults to False.
    """
    logging.basicConfig(
        level=getattr(logging, "DEBUG" if verbose else "INFO"),
        format="%(asctime)s %(levelname)s: %(message)s",
    )


# Based on tornado.ioloop.IOLoop.instance() approach.
# See https://github.com/facebook/tornado
# Whole idea for this metaclass is taken from: https://stackoverflow.com/a/6798042/2402281
class ThreadSafeSingletonMetaclass(type):
    _instances = {}
    _singleton_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # double-checked locking pattern (https://en.wikipedia.org/wiki/Double-checked_locking)
        if cls not in cls._instances:
            with cls._singleton_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(ThreadSafeSingletonMetaclass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
