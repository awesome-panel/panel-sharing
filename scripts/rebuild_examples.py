import shutil
from pathlib import Path
from panel_sharing.models import Project
from panel_sharing.components.gallery import _read_projects
from panel_sharing.utils import set_directory
import string

EXAMPLES_PATH = Path(__file__).parent.parent / "src/panel_sharing/examples"

def run():
    path = EXAMPLES_PATH
    for folder in path.iterdir():
        if folder.is_dir():
            with set_directory(folder):
                project = Project.read()
                project.rebuild(base_target="_blank")
            project.name = string.capwords(folder.name.replace("-", " "))
            shutil.copytree(src=project._tmppath, dst=folder, dirs_exist_ok=True)
            print(f"rebuilt {folder}")

if __name__=="__main__":
    run()
    