# panel serve apps/app.py --autoreload --static-dirs apps-dev=apps/dev/www apps=apps/prod/www
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

pn.extension("ace", notifications=True, exception_handler=exception_handler)

state = AppState()
state.build()

new_project_tab = components.NewProject()
configuration_tab = components.settings_editor(state)

build_and_share_project = components.BuildAndShareProject(state=state)
source_editor = components.SourceEditor(project=state.project)
editor_tab = pn.Column(
    build_and_share_project, source_editor, sizing_mode="stretch_both", name="Edit"
)

source_pane = pn.Tabs(
    new_project_tab,
    configuration_tab,
    editor_tab,
    components.faq,
    components.about,
    sizing_mode="stretch_both",
    active=2,
)

target_pane=components.iframe(src=state.param.development_url)

template = pn.template.FastGridTemplate(
    site=state.site.name,
    title=state.site.title,
    theme_toggle=False,
    prevent_collision=True,
    save_layout=True,
)
template.main[0:5, 0:6] = source_pane
template.main[0:5, 6:12] = target_pane
template.servable()
