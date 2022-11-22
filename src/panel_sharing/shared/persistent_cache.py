"""A simple persistent cache"""
import pickle
from pathlib import Path


class PersistentCache:
    """A simple persistent cache"""

    def __init__(self, path: Path):
        self._path = path.absolute()
        if not self._path.exists():
            self._path.mkdir(parents=True, exist_ok=True)

    def _file_path(self, key):
        return self._path / f"{key}.pickle"

    def __getitem__(self, key):
        path = self._file_path(key)
        if path.exists():
            with open(path, "rb") as handle:
                return pickle.load(handle)  # nosec:
        return {}

    def __setitem__(self, key, value):
        path = self._file_path(key)
        with open(path, "wb") as handle:
            pickle.dump(value, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def __delitem__(self, key):
        path = self._file_path(key)
        path.unlink()

    def __contains__(self, key):
        path = self._file_path(key)
        return path.exists()

    def get(self, key, default):
        """Returns the value if it exists. Otherwise returns default"""
        if key in self:
            return self[key]
        return default
