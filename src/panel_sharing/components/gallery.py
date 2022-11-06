"""The Gallery component enables users to select a project from a list of projects"""
import string
from pathlib import Path
from typing import List

import panel as pn

from panel_sharing.models import Gallery as GalleryModel
from panel_sharing.models import Project
from panel_sharing.utils import set_directory


def _read_projects(path: Path):
    examples = []
    for folder in path.iterdir():
        if folder.is_dir():
            with set_directory(folder):
                project = Project.read()
            project.name = string.capwords(folder.name.replace("-", " "))
            examples.append(project)
    return sorted(examples, key=lambda x: x.name)


class Gallery(GalleryModel, pn.viewable.Viewer):
    """Enables users to select a project from a list of projects"""

    def __init__(self, examples: List[Project], **params):
        super().__init__()

        layout = pn.Column(
            pn.pane.Markdown(
                "## 🎁 Examples\nClick a button below to select an example or check out the "
                "<fast-anchor href='sharing_gallery' appearance='hypertext'>Gallery</fast-anchor>.",
                margin=0,
            ),
            sizing_mode="stretch_width",
        )

        self._examples_map = {example.name: example for example in examples}

        self.value = self._examples_map.get("Welcome", examples[0])

        for example in examples:
            button = pn.widgets.Button(name=example.name, button_type="light")

            button.on_click(self._click_handler)
            layout.append(button)

        self._panel = layout

    def _click_handler(self, event):
        self.value = self._examples_map[event.obj.name]

    def __panel__(self):
        return self._panel

    @classmethod
    def read(cls, path: Path) -> "Gallery":
        """Returns a Gallery of projects read from the specified path"""
        examples = _read_projects(path)
        return cls(examples=examples)

    def get(self, name) -> Project:
        """Returns the project with the specified name"""
        return self._examples_map[name]


if __name__.startswith("bokeh"):
    pn.extension(template="fast")
    gallery = Gallery.read(Path(__file__).parent.parent / "examples")
    pn.Column(gallery.param.value, gallery).servable(target="sidebar")
