"""We have utility functions"""
from panel_sharing.utils import APP_KEY_PARAMETER, _get_app_key


def test_get_app_key_set():
    """We can get the app key"""
    key = "guest/basic"
    session_args = {APP_KEY_PARAMETER: [key.encode(encoding="utf8")]}
    assert _get_app_key(APP_KEY_PARAMETER, session_args) == key
