"""We can work with a Project"""
from io import BytesIO
from pathlib import Path

from panel_sharing import config
from panel_sharing.models import Project, Source
from panel_sharing.utils import set_directory


def test_build(tmpdir):
    """We can build a project"""
    project = Project()
    project.code = config.CODE
    project.requirements = config.REQUIREMENTS
    with set_directory(Path(tmpdir)):
        project.build()
        assert Path("source/app.py").exists()
        assert Path("source/readme.md").exists()
        assert Path("source/requirements.txt").exists()
        assert Path("build/config.json").exists()
        assert Path("build/app.html").exists()
        assert Path("build/app.js").exists()


def test_save_read(tmpdir):
    """We can save and read a project"""
    project = Project()
    project.source.code = "import panel"
    with set_directory(Path(tmpdir)):
        assert Path.cwd().exists()
        project.save()
        assert Path.cwd().exists()
        assert (Path(tmpdir) / "source/app.py").exists()

        new_project = Project.read()
    assert project.source.code == new_project.source.code


def test_base64():
    """We can convert a project to and from base64"""
    project = Project(
        name="Hello",
        source=Source(
            code="import panel",
            requirements="panel",
        ),
    )
    new_project = Project.from_base64(project.to_base64())
    assert new_project == project


def test_to_zip_folder():
    """We can convert between projects and zip folders"""
    # Given
    project = Project(
        source=Source(
            code="import panel as pn;pn.extension();pn.panel('hello').servable()",
            requirements="panel",
        )
    )
    # When
    zip_folder = project.to_zip_folder()
    # Assert
    assert isinstance(zip_folder, BytesIO)
    # When
    new_project = Project.from_zip_folder(zip_folder)
    # Then
    assert project == new_project


def test_tmpdir_deleted():
    """The tmpdir is deleted when the Project is deleted"""
    project = Project()
    tmpdir = project._tmpdir.name  # pylint: disable=protected-access
    assert tmpdir
    assert Path(tmpdir).exists()
    del project
    assert not Path(tmpdir).exists()
