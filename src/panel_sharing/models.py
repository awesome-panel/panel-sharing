"""Base models for Panel Sharing"""
# Should not contain any Panel UI elements
import json
import pathlib
import shutil
import tempfile
import uuid
from io import BytesIO
from typing import Dict

import param
from panel import __version__
from panel.io.convert import convert_apps

from panel_sharing import config
from panel_sharing.utils import set_directory


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


class Project(param.Parameterized):
    """A project consists of configuration and source files"""

    name = param.String(config.PROJECT_NAME)
    source = param.ClassSelector(class_=Source)

    def __init__(self, **params):
        if "source" not in params:
            params["source"] = Source()

        super().__init__(**params)

        if "name" not in params:
            with param.edit_constant(self):
                self.name = config.PROJECT_NAME

    def __str__(self):
        return self.name

    def save(self):
        """Saves the project files to the current working directory"""
        with set_directory(pathlib.Path() / "source"):
            self.source.save()

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
        return dict(
            apps=["source/app.py"],
            dest_path="build",
            runtime="pyodide-worker",
            requirements=self._get_requirements(),
            prerender=True,
            build_index=False,
            build_pwa=False,
            pwa_config={},
            verbose=False,
            max_workers=1,
        )

    def save_build_json(self, kwargs: Dict):
        """Saves the build configuration in a json file in the current working directory"""
        if not kwargs:
            kwargs = self._build_kwargs

        build_json = {
            "app_builder": {"awesome panel sharing": "0.0.0"},
            "app_framework": {"panel": __version__},
            "build_kwargs": kwargs,
        }
        with open("build.json", "w", encoding="utf8") as file:
            json.dump(obj=build_json, fp=file, indent=1)

    def build(self, base_target="", kwargs=None):
        """Saves and builds (i.e. converts) to the current working directory"""
        if not kwargs:
            kwargs = self._build_kwargs

        # We use `convert_apps` over `convert_app` due to
        # https://github.com/holoviz/panel/issues/3939
        convert_apps(**kwargs)
        self.save_build_json(kwargs)
        if base_target != "":
            app_html = pathlib.Path("build/app.html")
            text = app_html.read_text(encoding="utf8")
            text = text.replace("<head>", "<head><base target='_blank' />")
            app_html.write_text(text, encoding="utf8")


class User(param.Parameterized):
    """A User of the site"""

    name = param.String(config.USER_NAME, constant=True, regex=config.USER_NAME_REGEX)
    authenticated = param.Boolean(config.AUTHENTICATED, constant=True)

    def __init__(self, **params):
        super().__init__(**params)

        if "name" not in params:
            with param.edit_constant(self):
                self.name = config.USER_NAME

    def __str__(self):
        return self.name


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


class FileStorage(Storage):
    """The FileStorage represent a storage as files"""

    base_target = param.Selector(default="", objects=["", "_blank"])

    def __init__(self, path: str, **params):
        super().__init__(**params)

        self._path = pathlib.Path(path).absolute()

    def __getitem__(self, key):
        raise NotImplementedError()

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

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        raise NotImplementedError()

    def get_zipped_folder(self, key) -> BytesIO:
        """Returns the project as a .zip folder"""
        source = self._get_project_path(key).absolute()
        with tempfile.TemporaryDirectory() as tmpdir:
            with set_directory(pathlib.Path(tmpdir)):
                target_file = "saved"
                result = shutil.make_archive(target_file, "zip", source)
                with open(result, "rb") as file:
                    return BytesIO(file.read())


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

    def __getitem__(self, key):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        """Returns the list of keys of the storage"""
        raise NotImplementedError()


class Site(param.Parameterized):
    """A site like awesome-panel.org. But could also be another site"""

    name = param.String(config.SITE, constant=True)
    title = param.String(config.TITLE, constant=True)
    faq = param.String(config.FAQ, constant=True)
    about = param.String(config.ABOUT, constant=True)
    thumbnail = param.String(config.THUMBNAIL, constant=True)

    development_storage = param.ClassSelector(class_=Storage, constant=True)
    examples_storage = param.ClassSelector(class_=Storage, constant=True)
    production_storage = param.ClassSelector(class_=Storage, constant=True)

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
        return f"apps/{key}/app.html"

    def get_development_src(self, key):
        """Returns the development url"""
        return f"apps-dev/{key}/app.html"


class AppState(param.Parameterized):
    """Represents the state of the Sharing App"""

    site = param.Parameter(constant=True)
    user = param.Parameter(constant=True)
    project = param.Parameter(constant=True)

    development_key = param.String()
    development_url = param.String()

    shared_key = param.String()
    shared_url = param.String()

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


class Gallery(param.Parameterized):
    """Represents a Gallery of Projects"""

    value = param.ClassSelector(class_=Project)
