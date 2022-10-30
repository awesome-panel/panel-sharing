"""Create the Awesome Panel Sharing App"""
from __future__ import annotations

import panel as pn

from panel_sharing import components
from panel_sharing.models import AppState
from panel_sharing.utils import (
    exception_handler,
    get_app_key,
    get_example_key,
    notify_app_key_not_found,
)

RAW_CSS = """
.sidenav a {
    padding: 0px !important;
}
.sidenav a:hover {
    color: var(--accent-foreground-hover) !important;   
}
"""

if not "panel-sharing" in pn.state.cache:
    pn.state.cache["panel-sharing"] = {"state": {}}


def create():
    """Returns an instance of the Panel Sharing app

    Args:
        examples: A path to a gallery of example projects. Defaults to EXAMPLES.

    """
    pn.config.raw_css.append(RAW_CSS)
    pn.extension(
        "ace", sizing_mode="stretch_width", notifications=True, exception_handler=exception_handler
    )

    state = AppState()

    gallery = components.Gallery.read(state.examples)

    @pn.depends(gallery.param.value, watch=True)
    def set_example(project):
        state.copy(project, source=state.examples / project.source.name)
        pn.state.location.search = ""
        pn.state.location.update_query(example=project.name)

    key = get_app_key()
    example = get_example_key()
    if key:
        try:
            state.set_project_from_app_key(key)
            pn.state.location.search = ""
            pn.state.location.update_query(app=key)
        except:  # pylint: disable=bare-except
            notify_app_key_not_found("app", key)
            set_example(project=gallery.value)
            pn.state.location.search = ""
    else:
        try:
            set_example(project=gallery.get(example))
        except:  # pylint: disable=bare-except
            notify_app_key_not_found("example", key)
            set_example(project=gallery.value)
            pn.state.location.search = ""

    project_builder = components.ProjectBuilder(state=state)
    source_editor = components.SourceEditor(source=state.project.source)
    editor_tab = pn.Column(project_builder, source_editor, sizing_mode="stretch_both", name="Edit")

    source_pane = editor_tab

    target_pane = components.iframe(src=state.param.development_url)
    share_project = components.ShareProject(app_state=state, js_actions=project_builder.jsactions)

    authentication = components.OAuth()

    pn.bind(state.user.authenticate, name=authentication.param.user, watch=True)
    state.user.authenticate(authentication.user)

    @pn.depends(authentication.param.state, watch=True)
    def handle_auth_state(state, app_state=state):
        if not state:
            return
        cache = pn.state.cache["panel-sharing"]["state"]
        if not state in cache:
            cache[state] = {
                "source": app_state.project.source.to_dict(),
                "key": app_state.development_key,
            }
        else:
            app_state.project.source.param.update(**cache[state]["source"])
            app_state._set_development(cache[state]["key"])  # pylint: disable=protected-access

    login_state = pn.state.session_args.get("state", [b""])[0].decode("utf8")
    handle_auth_state(login_state)

    template = pn.template.FastGridTemplate(
        site=state.site.name,
        title=state.site.title,
        theme_toggle=False,
        prevent_collision=True,
        save_layout=True,
        site_url="https://awesome-panel.org",
        favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",  # pylint: disable=line-too-long
        sidebar=[
            share_project,
            authentication,
            gallery,
            project_builder.jsactions,
        ],
    )
    template.main[0:5, 0:6] = source_pane
    template.main[0:5, 6:12] = target_pane
    return template
