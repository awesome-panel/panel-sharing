from __future__ import annotations

import base64
import datetime as dt
import json
import logging
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import uuid

from pathlib import Path
from typing import Any, Dict

from panel_sharing import components
from panel_sharing import config
import param

from panel_sharing.models import AppState
from panel_sharing.utils import exception_handler

import panel as pn

from panel.io.convert import convert_apps
README = """## 📖 About

This is a first **prototype**.

**Your code and apps will be lost** when Panel Sharing is updated. Stay tuned for persisted
code and apps."""

RAW_CSS = """
.sidenav a {
    padding: 0px !important;
}
.sidenav a:hover {
    color: var(--accent-foreground-hover) !important;   
}
"""

EXAMPLES = Path(__file__).parent/"examples"

def create(examples: Path=EXAMPLES):
    pn.config.raw_css.append(RAW_CSS)
    pn.extension("ace", notifications=True, exception_handler=exception_handler)

    state = AppState()
    state.build()

    configuration_tab = components.settings_editor(state)

    build_and_share_project = components.BuildProject(state=state)
    source_editor = components.SourceEditor(project=state.project)
    editor_tab = pn.Column(
        build_and_share_project, source_editor, sizing_mode="stretch_both", name="Edit"
    )

    source_pane = editor_tab
        
    gallery = components.Gallery.create_from_project(examples)

    @pn.depends(gallery.param.value, watch=True)
    def update_project(project):
        source_editor.project.source.code = project.source.code
        source_editor.project.source.readme = project.source.readme
        source_editor.project.source.requirements = project.source.requirements
        build_and_share_project.convert=True
        print(project)

    target_pane=components.iframe(src=state.param.development_url)

    authentication = components.Authentication(app_state=state)
    share_project = components.ShareProject(app_state=state, js_actions=build_and_share_project.jsactions)

    template = pn.template.FastGridTemplate(
        site=state.site.name,
        title=state.site.title,
        theme_toggle=False,
        prevent_collision=True,
        save_layout=True,
        sidebar=[pn.Column(README), authentication, share_project, gallery, build_and_share_project.jsactions]
    )
    template.main[0:5, 0:6] = source_pane
    template.main[0:5, 6:12] = target_pane
    return template
