"""We have a simple persistent, thread and processs safe cache"""
from pathlib import Path

from panel_sharing.shared.persistent_cache import PersistentCache


def test_persistentdict(tmpdir):
    """We have a simple persistent, thread and processs safe cache"""
    cache = PersistentCache(path=Path(tmpdir) / "test")
    value = {"hello": "world"}

    cache["key"] = value
    assert cache["key"] == value
    del cache["key"]
    assert "key" not in cache
