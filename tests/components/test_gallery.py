import time
from pathlib import Path

from panel_sharing.components.gallery import _read_projects

EXAMPLES_PATH = Path(__file__).parent.parent.parent / "src/panel_sharing/examples"


def test_read_projects():
    projects = _read_projects(path=EXAMPLES_PATH)
    assert projects
    start = time.perf_counter()
    for project in projects:
        project.build()
    end = time.perf_counter()
    duration = end - start
    assert duration < 0.5
