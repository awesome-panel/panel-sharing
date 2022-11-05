"""Can can do CRUD operations for a project in Azure Blob Storage"""
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from panel_sharing.models import AppState, AzureBlobStorage, Project, Site, Source

# pylint: disable=redefined-outer-name,protected-access

PROJECT_CONTAINER_NAME = "test-project"
WEB_CONTAINER_NAME = "test-web"
WEB_URL = "https://awesomepanelsharing.blob.core.windows.net/test-web/"


@pytest.fixture
def key():
    """Returns a key"""
    return "MarcSkovMadsen/streamingvideo-interface"


@pytest.fixture()
def azure_blob_storage():
    """Returns an AzureBlobStorage"""
    return AzureBlobStorage(
        project_container_name=PROJECT_CONTAINER_NAME,
        web_container_name=WEB_CONTAINER_NAME,
        web_url=WEB_URL,
    )


@pytest.fixture()
def state(azure_blob_storage):
    """Returns an AppState relying on a production AzureBlobStorage"""
    site = Site(production_storage=azure_blob_storage)
    return AppState(site=site)


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
        ("config.json", False),
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
        ("config.json", PROJECT_CONTAINER_NAME),
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

    keys = azure_blob_storage.get_keys()
    assert keys == [key]

    azure_blob_storage.delete(key)

    for file in Project.files:
        url = azure_blob_storage.get_url(key, file)
        with pytest.raises(HTTPError):
            if url.startswith("https://"):
                with urlopen(url):  # nosec
                    pass


def test_state_site_get_shared_src(key: str, state: AppState):
    """We can get the right src for a shared app"""
    assert state.site.get_shared_src(key) == f"{WEB_URL}{key}/app.html"


def test_set_dev_project_from_shared_app(key: str, state: AppState, project: Project):
    """We can set the current dev project from a shared app key"""
    # Given
    state.site.production_storage[key] = project
    state.development_url = ""
    state.development_key = ""
    # When
    state.set_dev_project_from_shared_app(key)
    # Then
    assert state.development_url
    assert state.development_key
    # Clean Up
    state.site.production_storage.delete(key)
