"""A module of shared utilities"""
import logging
import os
import time
import urllib.parse as urlparse
from contextlib import ContextDecorator, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, Optional

import panel as pn

APP_KEY_PARAMETER = "app"
PROJECT_KEY_PARAMETER = "project"
DEFAULT_APP = ""
EXAMPLE_KEY_PARAMETER = "example"
DEFAULT_EXAMPLE = "Welcome"


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        path.mkdir(parents=True, exist_ok=True)
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def exception_handler(ex):
    """A general exception handler for panel apps"""
    logging.exception("Error", exc_info=ex)
    if pn.state.notifications and ex:
        pn.state.notifications.error(f"Error. {ex}")


def _get_app_key(key: str, session_args: Dict, default=""):
    if not key in session_args:
        return default
    try:
        return session_args[key][0].decode(encoding="utf8")
    except:  # pylint: disable=bare-except
        return default


def get_app_key(default=DEFAULT_APP):
    """Returns the value of the app session arg or the default value"""
    return _get_app_key(key=APP_KEY_PARAMETER, session_args=pn.state.session_args, default=default)


def get_project_key(default=""):
    """Returns the value of the project session arg or the default value"""
    return _get_app_key(
        key=PROJECT_KEY_PARAMETER, session_args=pn.state.session_args, default=default
    )


def get_example_key(default=DEFAULT_EXAMPLE):
    """Returns the value of the example session arg or the default value"""
    return _get_app_key(
        key=EXAMPLE_KEY_PARAMETER, session_args=pn.state.session_args, default=default
    )


def notify_app_key_not_found(app_or_example, key: str):
    """Helper function to notify the given key was not found on load"""
    notification = f"The {app_or_example} '{key}' was not found"

    def on_load():
        pn.state.notifications.error(notification)

    pn.state.onload(on_load)


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer(ContextDecorator):
    """Time your code using a class, context manager, or decorator"""

    # Source: https://realpython.com/python-timer/

    timers: ClassVar[Dict[str, float]] = {}
    name: Optional[str] = None
    text: str = "{}: Elapsed time: {:0.4f} seconds"
    logger: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialization: add timer to dict of timers"""
        if not self.name:
            self.name = "Timer"
        if self.name:
            self.timers.setdefault(self.name, 0)

    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger:
            self.logger(self.text.format(self.name, elapsed_time))
        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time

    def __enter__(self) -> "Timer":
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Stop the context manager timer"""
        self.stop()


def del_query_params(*args):
    """Deletes the query arguments"""
    if not args:
        args = ("code", "state", "example", "project", "app")
    if pn.state.location:
        query = pn.state.location.query_params
        for parameter in args:
            if parameter in query:
                del query[parameter]
        pn.state.location.search = "?" + urlparse.urlencode(query)
