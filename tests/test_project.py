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


def test_save_read(tmpdir):
    """We can save and read a project"""
    project = Project()
    project.source.code = "import panel"
    with set_directory(Path(tmpdir)):
        project.save()
        new_project = Project.read()
    assert project.source.code == new_project.source.code
