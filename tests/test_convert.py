"""We can convert a project"""
from pathlib import Path

import pytest

from panel_sharing.convert import ConversionError, _convert_project
from panel_sharing.models import Project
from panel_sharing.utils import set_directory


def convert_succeeded(tmpdir):
    """Returns True if the convert succeeded"""
    build_dir = Path(tmpdir) / "build"
    return (
        (build_dir / "app.html").exists()
        and (build_dir / "app.js").exists()
        and not "alert-convert-failed" in (build_dir / "app.html").read_text()
    )


def convert_failed(tmpdir):
    """Returns True if the convert failed"""
    return not convert_succeeded(tmpdir)


def test_can_convert(tmpdir):
    """We can convert a simple project"""
    project = Project()
    project.source.code = """
import panel as pn

pn.panel("hello").servable()
"""
    with set_directory(Path(tmpdir)):
        project.save()
        _convert_project()

    assert convert_succeeded(tmpdir)


def test_handle_import_not_found_error(tmpdir):
    """We create an app.html error report for failing code"""
    project = Project()
    project.source.code = """
import panel as pn

import a_non_installed_package
pn.panel("hello").servable()
"""
    with set_directory(Path(tmpdir)):
        project.save()
        with pytest.raises(ConversionError):
            _convert_project()

        assert convert_failed(tmpdir)


def test_handle_import_not_found_error2(tmpdir):
    """We create an app.html error report for failing code"""
    project = Project()
    project.source.code = """
import panel as pn

pn.panel("hello").servable()
import a_non_installed_package
"""
    with set_directory(Path(tmpdir)):
        project.save()
        with pytest.raises(ConversionError):
            _convert_project()

    assert convert_failed(tmpdir)
