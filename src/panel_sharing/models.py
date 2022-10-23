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

    def items(self) -> Dict:
        return {
            "app.py": self.code,
            "readme.md": self.readme,
            "thumbnail.png": self.thumbnail,
            "requirements.txt": self.requirements,
        }.items()

    def save(self):
        path = pathlib.Path()
        path.mkdir(parents=True, exist_ok=True)
        for file_path, text in self.items():
            pathlib.Path(path / file_path).write_text(text)


class Project(param.Parameterized):
    """A project consists of configuration and source files"""

    name = param.String(config.PROJECT_NAME)
    source = param.ClassSelector(class_=Source)

    def __init__(self, **params):
        if not "source" in params:
            params["source"] = Source()

        super().__init__(**params)

        if not "name" in params:
            with param.edit_constant(self):
                self.name = config.PROJECT_NAME

    def __str__(self):
        return self.name

    def save(self):
        with set_directory(pathlib.Path() / "source"):
            self.source.save()

    def _get_requirements(self):
        requirements = pathlib.Path("source/requirements.txt")
        if requirements.exists() and requirements.read_text():
            return str(requirements)
        else:
            return "auto"

    @property
    def build_kwargs(self) -> Dict:
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
        if not kwargs:
            kwargs = self.build_kwargs()

        build_json = {
            "app_builder": {"awesome panel sharing": "0.0.0"},
            "app_framework": {"panel": __version__},
            "build_kwargs": kwargs,
        }
        json.dump(obj=build_json, fp=open("build.json", "w"), indent=1)

    def build(self, base_target="", kwargs=None):
        if not kwargs:
            kwargs = self.build_kwargs

        # We use `convert_apps` over `convert_app` due to https://github.com/holoviz/panel/issues/3939
        convert_apps(**kwargs)
        self.save_build_json(kwargs)
        if base_target != "":
            app_html = pathlib.Path("build/app.html")
            text = app_html.read_text(encoding="utf8")
            text = text.replace("<head>", "<head><base target='_blank' />")
            app_html.write_text(text, encoding="utf8")


class User(param.Parameterized):
    name = param.String(config.USER_NAME, constant=True, regex=config.USER_NAME_REGEX)
    authenticated = param.Boolean(config.AUTHENTICATED, constant=True)

    def __init__(self, **params):
        super().__init__(**params)

        if not "name" in params:
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
        raise NotImplementedError()


class FileStorage(Storage):
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
                with open(result, "rb") as fh:
                    return BytesIO(fh.read())


class TmpFileStorage(FileStorage):
    pass


class AzureBlobStorage(Storage):
    pass


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
        if not "development_storage" in params:
            params["development_storage"] = TmpFileStorage(path="apps/dev", base_target="_blank")
        if not "examples_storage" in params:
            params["examples_storage"] = FileStorage(path="apps/examples")
        if not "production_storage" in params:
            params["production_storage"] = FileStorage(path="apps/prod")

        super().__init__(**params)

        if not "name" in params:
            with param.edit_constant(self):
                self.name = config.SITE

    def get_shared_key(self, user: User, project: Project):
        return user.name + "/" + project.name

    def get_shared_src(self, key):
        return f"apps/{key}/app.html"

    def get_development_src(self, key):
        return f"apps-dev/{key}/app.html"


class AppState(param.Parameterized):
    """Represents the state of the Sharing App"""

    site = param.Parameter(constant=True)
    user = param.Parameter(constant=True)
    project = param.Parameter(constant=True)

    # Todo: make the below constant
    # could not do it as it raised an error!
    development_key = param.String()
    development_url = param.String()

    shared_key = param.String()
    shared_url = param.String()

    def __init__(self, **params):
        if not "site" in params:
            params["site"] = Site()
        if not "user" in params:
            params["user"] = User()
        if not "project" in params:
            params["project"] = Project()

        super().__init__(**params)

    def _set_development(self, key: str):
        self.development_key = key
        self.development_url = self.site.get_development_src(key)

    def set_shared(self, key: str):
        self.shared_key = key
        self.shared_url = self.site.get_shared_src(key)

    @param.depends("user.name", "project.name", watch=True, on_init=True)
    def _update_shared(self):
        key = self.site.get_shared_key(user=self.user, project=self.project)
        self.set_shared(key)

    def _get_random_key(self):
        return str(uuid.uuid4())

    def build(self):
        # We need to use a new key to trigger the iframe to refresh
        # The panel server somehow messes with the file
        key = self._get_random_key()
        self.site.development_storage[key] = self.project
        self._set_development(key)
        print("build")

    def share(self):
        key = self.shared_key
        url = self.shared_url
        self.site.production_storage[key] = self.project
        return url

    def login(self):
        with param.edit_constant(self.user):
            self.user.authenticated = True

    def logout(self):
        with param.edit_constant(self.user):
            self.user.authenticated = False


class Gallery(param.Parameterized):
    value = param.ClassSelector(class_=Project)
