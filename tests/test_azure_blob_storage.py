"""Can can do CRUD operations for a project in Azure Blob Storage"""
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from panel_sharing.models import AzureBlobStorage, Project, Source

# pylint: disable=redefined-outer-name,protected-access

PROJECT_CONTAINER_NAME = "test-project"
WEB_CONTAINER_NAME = "test-web"


@pytest.fixture
def key():
    """Returns a key"""
    return "MarcSkovMadsen/streamingvideo-interface"


@pytest.fixture()
def azure_blob_storage():
    """Returns an AzureBlobStorage"""
    return AzureBlobStorage(
        project_container_name=PROJECT_CONTAINER_NAME, web_container_name=WEB_CONTAINER_NAME
    )


@pytest.fixture()
def project():
    """Returns a Project"""
    return Project(
        name="some project",
        source=Source(
            code="import panel as pn;pn.panel('hello').servable()",
            readme="Hi there",
            requirements="panel",
        ),
    )


@pytest.mark.parametrize(
    ["file", "is_build_file"],
    (
        ("build.json", False),
        ("source/app.py", False),
        ("source/requirements.txt", False),
        ("build/app.html", True),
        ("build/app.js", True),
    ),
)
def test_is_build_file(file, is_build_file, azure_blob_storage):
    """We can determine if a file is a build file"""
    assert azure_blob_storage._is_build_file(file) == is_build_file


@pytest.mark.parametrize(
    ["file", "container_name"],
    (
        ("build.json", PROJECT_CONTAINER_NAME),
        ("source/app.py", PROJECT_CONTAINER_NAME),
        ("source/requirements.txt", PROJECT_CONTAINER_NAME),
        ("build/app.html", WEB_CONTAINER_NAME),
        ("build/app.js", WEB_CONTAINER_NAME),
    ),
)
def test_get_container_name(file, container_name, azure_blob_storage):
    """We can get the name of the container a file should be saved to"""
    assert azure_blob_storage._get_container_name(file) == container_name


def test_set_and_get(key: str, azure_blob_storage: AzureBlobStorage, project: Project):
    """We can set and get a project"""
    azure_blob_storage[key] = project

    for file in Project.files:
        url = azure_blob_storage.get_url(key, file)
        if url.startswith("https://"):
            with urlopen(url) as response:  # nosec
                assert response.status == 200

    new_project = azure_blob_storage[key]
    assert project == new_project

    azure_blob_storage.delete(key)

    for file in Project.files:
        url = azure_blob_storage.get_url(key, file)
        with pytest.raises(HTTPError):
            if url.startswith("https://"):
                with urlopen(url):  # nosec
                    pass
