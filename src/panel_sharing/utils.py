"""A module of shared utilities"""
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Dict

import panel as pn

APP_KEY_PARAMETER = "app"
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
