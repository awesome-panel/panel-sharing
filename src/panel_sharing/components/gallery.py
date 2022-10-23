from pathlib import Path
from typing import List

import panel as pn
import param

from panel_sharing.models import Gallery as GalleryModel
from panel_sharing.models import Project, Source
import string


def read_projects(path: Path):
    examples = []
    for folder in path.iterdir():
        if folder.is_dir():
            project = Project(
                name=string.capwords(folder.name.replace("-", " ")),
                source=Source(
                    name=folder.name,
                    code=(folder/"source/app.py").read_text(),
                    readme=(folder/"source/readme.md").read_text(),
                    requirements=(folder/"source/requirements.txt").read_text(),
                ),
            ) 
            examples.append(project)
    return sorted(examples, key=lambda x: x.name)

class Gallery(GalleryModel, pn.viewable.Viewer):

    def __init__(self, examples: List[Project], **params):
        super().__init__()

        self.value = examples[0]

        layout = pn.Column(
            pn.pane.Markdown("## 🎁 Examples"),
            sizing_mode="stretch_width",
        )
        
        self._examples_map = {example.name: example for example in examples}
        
        for example in examples:
            button = pn.widgets.Button(name=example.name, button_type="success")
            
            button.on_click(self._click_handler)
            layout.append(button)
        
        
        self._panel = layout

    def _click_handler(self, event):
        self.value = self._examples_map[event.obj.name]
        print("click handled")
    
    def __panel__(self):
        return self._panel

    @classmethod
    def create_from_project(cls, path: Path)->'Gallery':
        examples = read_projects(path)
        return cls(examples=examples)

if __name__.startswith("bokeh"):
    pn.extension(template="fast")
    gallery = Gallery()
    pn.Column(gallery.param.value, gallery).servable(target="sidebar")
