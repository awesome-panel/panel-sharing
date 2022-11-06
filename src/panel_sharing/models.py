"""Base models for Panel Sharing"""
# Should not contain any Panel UI elements
from __future__ import annotations

import base64
import json
import multiprocessing
import pathlib
import shutil
import tempfile
import uuid
from io import BytesIO
from pathlib import Path
from typing import Dict, List

import param
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.blob._list_blobs_helper import BlobPrefix
from panel import __version__
from panel.io.convert import convert_app

from panel_sharing import VERSION, config
from panel_sharing.utils import Timer, set_directory

ctx_forkserver = multiprocessing.get_context("forkserver")
ctx_forkserver.set_forkserver_preload(
    [
        # "base64",
        "bokeh",
        "holoviews",
        "hvplot",
        # "io",
        # "matplotlib",
        "numpy",
        "pandas",
        "panel",
        "param",
        # "PIL",
        # "skimage",
    ]
)

EXAMPLES = Path(__file__).parent / "examples"


def _convert_project(app: str = "source/app.py", dest_path: str = "build", requirements="auto"):
    """Helper function"""
    Path(dest_path).mkdir(parents=True, exist_ok=True)
    convert_app(app=Path(app), dest_path=Path(dest_path), requirements=requirements)  # type: ignore


class Source(param.Parameterized):
    """Represent the source files"""

    name = param.String(config.REPOSITORY_NAME, constant=True)
    code = param.String(config.CODE)
    readme = param.String(config.README)
    thumbnail = param.String(config.THUMBNAIL)
    requirements = param.String(config.REQUIREMENTS)

    def _items(self):
        """Returns the list of filename: text value"""
        return {
            "app.py": self.code,
            "readme.md": self.readme,
            "thumbnail.png": self.thumbnail,
            "requirements.txt": self.requirements,
        }.items()

    def save(self):
        """Saves the source files to the current working directory"""
        path = pathlib.Path()
        path.mkdir(parents=True, exist_ok=True)
        for file_path, text in self._items():
            pathlib.Path(path / file_path).write_text(text, encoding="utf8")

    @classmethod
    def read(cls) -> "Source":
        """Reads the Source from the current working directory"""
        path = pathlib.Path()
        source = cls(name="new")
        source.code = (path / "app.py").read_text()
        source.readme = (path / "readme.md").read_text()
        source.requirements = (path / "requirements.txt").read_text()
        return source

    def to_dict(self) -> Dict:
        """Returns the source as a dict"""
        return {
            "code": self.code,
            "readme": self.readme,
            # "thumbnail": self.thumbnail,
            "requirements": self.requirements,
        }


class Project(param.Parameterized):
    """A project consists of configuration and source files"""

    name = param.String(config.PROJECT_NAME)
    source = param.ClassSelector(class_=Source)
    files = param.Tuple(
        default=(
            "source/app.py",
            "source/requirements.txt",
            "source/readme.md",
            "source/thumbnail.png",
            "build/config.json",
            "build/app.html",
            "build/app.js",
        )
    )

    def __init__(self, **params):
        if "source" not in params:
            params["source"] = Source()
        super().__init__(**params)

        self._tmpdir = tempfile.TemporaryDirectory() # pylint: disable=consider-using-with
        self._tmppath = Path(self._tmpdir.name)
        self._save_hash = ""
        self._build_hash = ""

        if "name" not in params:
            with param.edit_constant(self):
                self.name = config.PROJECT_NAME

    def __del__(self):
        self._tmpdir.cleanup()

    def __str__(self):
        return self.name

    @classmethod
    def read(cls) -> "Project":
        """Reads the Project from the current working directory"""
        project = Project(name="new")
        with set_directory(Path("source")):
            project.source = Source.read()
        shutil.copytree(Path(), Path(project._tmpdir.name), dirs_exist_ok=True)
        project._save_hash=project._hash
        if Path("build").exists():
            project._build_hash=project._hash
        return project

    @property
    def _hash(self):
        return hash(json.dumps(self.to_dict()))

    def _reset_tmpdir(self):
        self._save_hash=""
        self._build_hash=""
        for child in self._tmppath.iterdir():
            if child.is_file():
                child.unlink()
            else:
                shutil.rmtree(child)

    def _save_to_tmpdir(self):
        _hash = self._hash
        if self._save_hash==_hash:
            return

        self._reset_tmpdir()
        with set_directory(self._tmppath/"source"):
            self.source.save()
        self._save_hash = _hash

    def save(self):
        """Saves the project files to the current working directory"""
        self._save_to_tmpdir()
        self._copy_from_tmpdir()

    def _get_requirements(self):
        requirements = pathlib.Path("source/requirements.txt")
        if requirements.exists() and requirements.read_text(encoding="utf8"):
            return str(requirements)
        return "auto"

    @property
    def _build_kwargs(self) -> Dict:
        """

        Assumes we are in the Project root and the source files are in ./source

        Returns:
            _description_
        """
        return {
            "app": "source/app.py",
            "dest_path": "build",
            "requirements": self._get_requirements(),
        }

    def save_build_json(self, kwargs: Dict):
        """Saves the build configuration in a json file in the current working directory"""
        if not kwargs:
            kwargs = self._build_kwargs

        build_json = {
            "app_builder": {"panel sharing": VERSION},
            "app_framework": {"panel": __version__},
            "build_kwargs": kwargs,
        }
        with open("config.json", "w", encoding="utf8") as file:
            json.dump(obj=build_json, fp=file, indent=1)

    def _remove_tmpbuilddir(self):
        self._build_hash=""
        tmpbuildpath = self._tmppath/"build"
        if tmpbuildpath.exists():
            shutil.rmtree(tmpbuildpath)

    def _build_to_tmpdir(self, base_target):
        _hash = self._hash + hash(base_target)
        if self._build_hash==_hash:
            return

        self._remove_tmpbuilddir()
        with set_directory(self._tmppath):
            kwargs = self._build_kwargs

            # We need to be really careful when we convert. See
            # https://github.com/holoviz/panel/issues/3939
            with Timer("convert project"):
                process = ctx_forkserver.Process(
                    target=_convert_project,
                    kwargs=kwargs,
                )
                process.start()

                with set_directory(Path("build")):
                    self.save_build_json(kwargs)
                process.join()
                if base_target != "":
                    app_html = Path("build/app.html")
                    text = app_html.read_text(encoding="utf8")
                    text = text.replace("<head>", "<head><base target='_blank' />")
                    app_html.write_text(text, encoding="utf8")

        self._build_hash = _hash

    def _copy_from_tmpdir(self):
        dst = str(Path().absolute())
        shutil.copytree(self._tmppath, dst, dirs_exist_ok=True)

    def build(self, base_target=""):
        """Saves and builds (i.e. converts) to the current working directory"""
        self._save_to_tmpdir()
        self._build_to_tmpdir(base_target=base_target)
        self._copy_from_tmpdir()



    def to_dict(self):
        """Returns the project as a dictionary"""
        return {"source": self.source.to_dict()}

    def to_base64(self):
        """Returns the project base64 encoded"""
        value = json.dumps(self.to_dict(), separators=(",", ":"))
        result = base64.b64encode(value.encode(encoding="utf8")).decode(encoding="utf8")
        print("base64 len", len(result))
        return result

    @classmethod
    def from_dict(cls, value: Dict) -> "Project":
        """Returns a project from the value provided"""
        source = value.pop("source")
        return Project(source=Source(**source))

    @classmethod
    def from_base64(cls, value: str) -> "Project":
        """Returns a project from the base64 value"""
        value_dict = json.loads(base64.b64decode(value).decode(encoding="utf8"))
        return cls.from_dict(value_dict)

    def __eq__(self, other):
        return isinstance(other, Project) and self.to_dict() == other.to_dict()

    def to_zip_folder(self) -> BytesIO:
        """Returns the project as a .zip folder"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with set_directory(pathlib.Path(tmpdir)):
                with set_directory(pathlib.Path("project")):
                    self.save()
                    self.build()
                target_file = "saved"
                result = shutil.make_archive(
                    target_file, "zip", root_dir=Path("project").absolute()
                )
                with open(result, "rb") as file:
                    return BytesIO(file.read())

    @staticmethod
    def from_zip_folder(zip_folder: BytesIO):
        """Creates a Project from a zip_folder"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with set_directory(pathlib.Path(tmpdir)):
                target_file = "saved.zip"
                with open(target_file, "wb") as file:
                    file.write(zip_folder.getbuffer())
                    shutil.unpack_archive(target_file, format="zip")
                    return Project.read()

    def copy(self, project: Project):
        """Copies the given project including any saved and build files"""
        self.source.code = project.source.code
        self.source.readme = project.source.readme
        self.source.requirements = project.source.requirements
        self.source.thumbnail = project.source.thumbnail
        self._save_hash=""
        self._build_hash=""
        self._reset_tmpdir()

        # pylint: disable=protected-access
        with set_directory(self._tmppath):
            project._copy_from_tmpdir()
        self._save_hash=project._save_hash
        self._build_hash=project._build_hash




class User(param.Parameterized):
    """A User of the site"""

    name = param.String(config.GUEST_USER_NAME, constant=True, regex=config.USER_NAME_REGEX)
    authenticated = param.Boolean(config.AUTHENTICATED, constant=True)

    def __init__(self, **params):
        super().__init__(**params)

        if "name" not in params:
            with param.edit_constant(self):
                self.name = config.GUEST_USER_NAME

    def __str__(self):
        return self.name

    def authenticate(self, name):
        """Authenticates the give name"""
        with param.edit_constant(self):
            if name and name != config.GUEST_USER_NAME:
                self.name = name
                self.authenticated = True
            else:
                self.name = config.GUEST_USER_NAME
                self.authenticated = False


class Storage(param.Parameterized):
    """Represent a key-value where the value is a Project"""

    def __getitem__(self, key):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        """Returns the list of keys of the storage"""
        raise NotImplementedError()

    def copy(self, key: str, project: Project):
        """Copy the source project to the specified key"""
        raise NotImplementedError()


class FileStorage(Storage):
    """The FileStorage represent a storage as files"""

    base_target = param.Selector(default="", objects=["", "_blank"])

    def __init__(self, path: str, **params):
        super().__init__(**params)

        self._path = pathlib.Path(path).absolute()

    def __getitem__(self, key):
        with set_directory(self._path / "projects" / key):
            project = Project.read()
        return project

    def _get_project_path(self, key) -> pathlib.Path:
        return self._path / "projects" / key

    def _get_www_path(self, key) -> pathlib.Path:
        return self._path / "www" / key

    def _move_locally(self, tmppath: pathlib.Path, project: pathlib.Path, www: pathlib.Path):
        if project.exists():
            shutil.rmtree(project)
        shutil.copytree(tmppath, project)
        if www.exists():
            shutil.rmtree(www)
        shutil.copytree(tmppath / "build", www)

    def __setitem__(self, key: str, value: Project):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = pathlib.Path(tmpdir)
            with set_directory(tmppath):
                value.save()
                value.build(base_target=self.base_target)

            project = self._get_project_path(key)
            www = self._get_www_path(key)

            self._move_locally(tmppath, project, www)

    def copy(self, key: str, project: Project):
        project_dir = self._get_project_path(key)
        www_dir = self._get_www_path(key)

        with tempfile.TemporaryDirectory() as source:
            source_path = Path(source)
            with set_directory(source_path):
                project.save()
                project.build()
                self._move_locally(source_path, project_dir, www_dir)

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()


class TmpFileStorage(FileStorage):
    """A FileStorage with temporary files that are cleaned up when no longer in use"""

    def __getitem__(self, key):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()


class AzureBlobStorage(Storage):
    """An Azure Blob Storage"""

    base_target = param.Selector(default="", objects=["", "_blank"])
    blob_url = param.String(default=config.AZURE_BLOB_URL)
    web_url = param.String(default=config.AZURE_WEB_URL)
    project_container_name = param.String(default=config.AZURE_PROJECT_CONTAINER_NAME)
    web_container_name = param.String(default=config.AZURE_WEB_CONTAINER_NAME)
    conn_str = param.String(default=config.AZURE_BLOB_CONN_STR)

    def __init__(self, **params):
        super().__init__(**params)

        if not self.conn_str:
            raise ValueError("Error. No conn_str provided!")

        # Create the BlobServiceClient object
        self.service_client = BlobServiceClient.from_connection_string(self.conn_str)
        self.project_container_client = self.service_client.get_container_client(
            self.project_container_name
        )
        self.web_container_client = self.service_client.get_container_client(
            self.web_container_name
        )

    def __getitem__(self, key):
        with tempfile.TemporaryDirectory() as tmpdir:
            with set_directory(Path(tmpdir)):
                self._save_locally(key)
                return Project.read()

    def _save_locally(self, key: str):
        prefix = key + "/"

        project_generator = self.project_container_client.list_blobs(name_starts_with=prefix)
        for blob in project_generator:
            file = blob.name.replace(prefix, "")
            Path(file).parent.mkdir(parents=True, exist_ok=True)
            with open(file=file, mode="wb") as download_file:
                download_file.write(
                    self.project_container_client.download_blob(blob.name).readall()
                )

        web_generator = self.web_container_client.list_blobs(name_starts_with=prefix)
        for blob in web_generator:
            file = blob.name.replace(prefix, "build/")
            Path(file).parent.mkdir(parents=True, exist_ok=True)
            with open(file=file, mode="wb") as download_file:
                try:
                    download_file.write(
                        self.web_container_client.download_blob(blob.name).readall()
                    )
                except ResourceNotFoundError as ex:
                    raise Exception(
                        f"The container {self.web_container_name} or blob {blob} was not found"
                    ) from ex

    @staticmethod
    def _is_build_file(file: Path):
        return str(file).startswith("build/")

    def _get_container_name(self, file: Path):
        if self._is_build_file(file):
            return self.web_container_name
        return self.project_container_name

    def _get_file_path(self, file: Path):
        if self._is_build_file(file):
            return Path(file.name)
        return file

    def _get_blob(self, key: str, file: Path):
        file_path = self._get_file_path(file)
        return key + "/" + str(file_path)

    def _get_blob_client(self, key: str, file: Path):
        container_name = self._get_container_name(file)
        blob = self._get_blob(key, file)
        return self.service_client.get_blob_client(container=container_name, blob=blob)

    def _get_content_settings(self, file: Path) -> ContentSettings | None:
        if file.name.endswith("html"):
            return ContentSettings(content_type="text/html")
        return None

    def __setitem__(self, key, value: Project):
        with tempfile.TemporaryDirectory() as tmpdir:
            with set_directory(Path(tmpdir)):
                value.save()
                value.build(self.base_target)
                for file in Path().rglob("*"):
                    if file.is_file():
                        blob_client = self._get_blob_client(key=key, file=file)
                        content_settings = self._get_content_settings(file)
                        with open(file, mode="rb") as data:
                            blob_client.upload_blob(
                                data, overwrite=True, content_settings=content_settings
                            )

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        """Returns the list of keys of the storage"""
        raise NotImplementedError()

    def copy(self, key: str, project: Project):
        raise NotImplementedError()
        # project = self._get_project_path(key)
        # www = self._get_www_path(key)
        # self._move_locally(source, project, www)

    def delete(self, key):
        """Delete the key"""
        for file_ in Project.files:
            file = Path(file_)
            blob = self._get_blob(key=key, file=file)
            container_name = self._get_container_name(file)
            blob_client = self.service_client.get_blob_client(container=container_name, blob=blob)
            blob_client.delete_blob(snapshot=None)

    def get_url(self, key, file):
        """Returns the app url of the given key and file"""
        file = Path(file)
        container_name = self._get_container_name(file)
        file_path = self._get_file_path(file)
        if container_name == "$web":
            return self.web_url + key + "/" + str(file_path)
        return self.blob_url + container_name + "/" + key + "/" + str(file_path)


    def get_keys(self) -> List[str]:
        """Returns the app keys from the blob storage"""
        keys = []
        for user in self.web_container_client.walk_blobs('', delimiter='/'):
            if isinstance(user, BlobPrefix):
                for app in user:
                    if isinstance(app, BlobPrefix):
                        keys.append(app.name[:-1])
        return keys


class Site(param.Parameterized):
    """A site like awesome-panel.org. But could also be another site"""

    name: str = param.String(config.SITE, constant=True)
    title: str = param.String(config.TITLE, constant=True)
    faq: str = param.String(config.FAQ, constant=True)
    about: str = param.String(config.ABOUT, constant=True)
    thumbnail: str = param.String(config.THUMBNAIL, constant=True)

    development_storage: Storage = param.ClassSelector(class_=Storage, constant=True)
    examples_storage: Storage = param.ClassSelector(class_=Storage, constant=True)
    production_storage: Storage = param.ClassSelector(class_=Storage, constant=True)

    auth_provider = param.Parameter(constant=True)

    def __init__(self, **params):
        if "development_storage" not in params:
            params["development_storage"] = TmpFileStorage(path="apps/dev", base_target="_blank")
        if "examples_storage" not in params:
            params["examples_storage"] = FileStorage(path="apps/examples")
        if "production_storage" not in params:
            params["production_storage"] = FileStorage(path="apps/prod")

        super().__init__(**params)

        if "name" not in params:
            with param.edit_constant(self):
                self.name = config.SITE

    def get_shared_key(self, user: User, project: Project) -> str:
        """Returns the key of the user and project"""
        return user.name + "/" + project.name

    def get_shared_src(self, key):
        """Returns the shared url"""
        if isinstance(self.production_storage, AzureBlobStorage):
            return self.production_storage.get_url(key, "build/app.html")
        return f"apps/{key}/app.html"

    def get_development_src(self, key):
        """Returns the development url"""
        return f"apps-dev/{key}/app.html"


class AppState(param.Parameterized):
    """Represents the state of the Sharing App"""

    site: Site = param.Parameter(constant=True)
    user: User = param.Parameter(constant=True)
    project: Project = param.Parameter(constant=True)

    development_key: str = param.String()
    development_url: str = param.String()

    shared_key: str = param.String()
    shared_url: str = param.String()

    examples: pathlib.Path = param.ClassSelector(default=EXAMPLES, class_=pathlib.Path)

    def __init__(self, **params):
        if "site" not in params:
            params["site"] = Site()
        if "user" not in params:
            params["user"] = User()
        if "project" not in params:
            params["project"] = Project()

        super().__init__(**params)

    def _set_development(self, key: str):
        self.development_key = key
        if not key:
            self.development_url = ""
        else:
            self.development_url = self.site.get_development_src(key)

    def set_shared(self, key: str):
        """Sets the shared_key and shared_url"""
        self.shared_key = key
        self.shared_url = self.site.get_shared_src(key)

    @param.depends("user.name", "project.name", watch=True, on_init=True)
    def _update_shared(self):
        key = self.site.get_shared_key(user=self.user, project=self.project)
        self.set_shared(key)

    def _get_random_key(self):
        return str(uuid.uuid4())

    def copy(self, project: Project):
        """Copies the project from the source path"""
        self.project.copy(project)

        key = self._get_random_key()
        self.site.development_storage.copy(key=key, project=self.project)
        self._set_development(key)

    def build(self):
        """Build the current project and reload the app"""
        # We need to use a new key to trigger the iframe to refresh
        # The panel server somehow messes with the file
        self._set_development("")
        key = self._get_random_key()
        self.site.development_storage[key] = self.project
        self._set_development(key)

    def share(self):
        """Shared the current project"""
        key = self.shared_key
        url = self.shared_url
        self.site.production_storage[key] = self.project
        return url

    def login(self):
        """Logs the user in"""
        with param.edit_constant(self.user):
            self.user.authenticated = True

    def logout(self):
        """Logs the user out"""
        with param.edit_constant(self.user):
            self.user.authenticated = False

    def set_dev_project_from_shared_app(self, key):
        """Set the current project from an app key"""
        project = self.site.production_storage[key]

        self.project.source.code = project.source.code
        self.project.source.readme = project.source.readme
        self.project.source.requirements = project.source.requirements

        # pylint: disable=protected-access
        key = self._get_random_key()

        self.site.development_storage.copy(key=key, project=project)
        self._set_development(key)


class Gallery(param.Parameterized):
    """Represents a Gallery of Projects"""

    value = param.ClassSelector(class_=Project)
