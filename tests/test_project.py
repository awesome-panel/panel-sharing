"""We can work with a Project"""
from pathlib import Path

from panel_sharing import config
from panel_sharing.models import Project
from panel_sharing.utils import set_directory


def test_build(tmpdir):
    """We can build a project"""
    project = Project()
    project.code = config.CODE
    project.requirements = config.REQUIREMENTS
    with set_directory(Path(tmpdir)):
        project.save()
        project.build()
        assert Path("build.json").exists()
        assert Path("source/app.py").exists()
        assert Path("source/readme.md").exists()
        assert Path("source/requirements.txt").exists()
        assert Path("build/app.html").exists()
