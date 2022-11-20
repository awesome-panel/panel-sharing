"""We have utility functions"""
from pathlib import Path

import pytest

from panel_sharing.utils import APP_KEY_PARAMETER, _get_app_key, set_directory


def test_get_app_key_set():
    """We can get the app key"""
    key = "guest/basic"
    session_args = {APP_KEY_PARAMETER: [key.encode(encoding="utf8")]}
    assert _get_app_key(APP_KEY_PARAMETER, session_args) == key


def test_set_directory_can_handle_exception(tmpdir):
    """We can temporarily change the cwd

    We will also get back to original cwd even though a exception was raised during the change
    """
    before = Path.cwd().absolute()

    with pytest.raises(ValueError):
        with set_directory(Path(tmpdir)):
            assert Path.cwd().absolute() == Path(tmpdir)
            raise ValueError("an error occured")

    assert Path.cwd().absolute() == before
