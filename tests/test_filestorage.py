"""We can work with a FileStorage"""

from panel_sharing.models import FileStorage, Project


def test_set_and_get_project(tmpdir):
    """We can set and get a project"""
    project = Project()
    project.source.code = "import panel"
    project.source.requirements = "panel"
    project.source.readme = "hello"
    key = "test"
    storage = FileStorage(tmpdir)

    storage[key] = project
    new_project = storage[key]
    assert project.source.code == new_project.source.code
    assert project.source.requirements == new_project.source.requirements
    assert project.source.readme == new_project.source.readme
