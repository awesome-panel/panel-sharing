"""Create the Awesome Panel Sharing App"""
from __future__ import annotations

import logging
from pathlib import Path

import panel as pn
from diskcache import Cache

from panel_sharing import components
from panel_sharing.models import AppState, AzureBlobStorage, Project, Site
from panel_sharing.utils import (
    exception_handler,
    get_app_key,
    get_example_key,
    get_project_key,
    notify_app_key_not_found,
)

logger = logging.getLogger("panel_sharing")
logger.setLevel(logging.INFO)

RAW_CSS = """
.sidenav a {
    padding: 0px !important;
}
.sidenav a:hover {
    color: var(--accent-foreground-hover) !important;   
}
"""


cache = Cache(".cache/panel_sharing")


@pn.cache
def get_examples(examples: str):
    """Returns a list of example Projects"""
    # pylint: disable=protected-access
    return list(components.Gallery.read(Path(examples))._examples_map.values())


def _set_start_project(state, set_example, gallery):
    key = get_app_key()
    project = get_project_key()
    example = get_example_key()
    if key:
        try:
            state.set_dev_project_from_shared_app(key)
        except:  # pylint: disable=bare-except
            notify_app_key_not_found("app", key)
            set_example(project=gallery.value)
            pn.state.location.search = ""
    elif project:
        try:
            project_ = Project.from_base64(project)
            state.project.source.code = project_.source.code
            state.project.source.requirements = project_.source.requirements
            state.project.source.readme = project_.source.readme
            state.project.source.thumbnail = project_.source.thumbnail
            pn.state.onload(state.build)
        except:  # pylint: disable=bare-except
            notify_app_key_not_found("project", key)
            set_example(project=gallery.value)
            pn.state.location.search = ""
    else:
        try:
            set_example(project=gallery.get(example))
        except:  # pylint: disable=bare-except
            notify_app_key_not_found("example", key)
            set_example(project=gallery.value)
            pn.state.location.search = ""


def create():
    """Returns an instance of the Panel Sharing app

    Args:
        examples: A path to a gallery of example projects. Defaults to EXAMPLES.

    """
    logger.info("CREATE STARTED")
    pn.config.raw_css.append(RAW_CSS)
    pn.extension(
        "ace", sizing_mode="stretch_width", notifications=True, exception_handler=exception_handler
    )

    site = Site(production_storage=AzureBlobStorage())
    state = AppState(site=site)

    gallery = components.Gallery(examples=get_examples(str(state.examples.absolute())))

    @pn.depends(gallery.param.value, watch=True)
    def set_example(project):
        project.build()
        state.copy(project)
        if pn.state.location:
            logger.info("set_example: updating location")
            pn.state.location.search = ""
            pn.state.location.update_query(example=project.name)

    _set_start_project(state, set_example, gallery)

    project_builder = components.ProjectBuilder(state=state)
    source_editor = components.SourceEditor(source=state.project.source)
    editor_tab = pn.Column(project_builder, source_editor, sizing_mode="stretch_both", name="Edit")

    source_pane = editor_tab

    target_pane = components.iframe(src=state.param.development_url)
    # pylint: disable=line-too-long
    getting_started = pn.Column(
        pn.pane.Markdown(
            """## 🏃 Get Started

Check out the <fast-anchor href="https://github.com/awesome-panel/panel-sharing/blob/main/docs/user-guide.md" appearance="hypertext" class="hypertext" target="_blank">User Guide</fast-anchor>
and report issues at <fast-anchor href="https://github.com/awesome-panel/panel-sharing" appearance="hypertext" class="hypertext" target="_blank">panel-sharing</fast-anchor>.
""",
            margin=0,
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
        margin=0,
    )
    # pylint: enable=line-too-long
    share_project = components.ShareProject(app_state=state, js_actions=project_builder.jsactions)

    authentication = components.OAuth()

    pn.bind(state.user.authenticate, name=authentication.param.user, watch=True)
    logger.info("authenticating user")
    state.user.authenticate(authentication.user)

    @pn.depends(authentication.param.state, watch=True)
    def handle_auth_state(state, app_state=state):
        logger.info("handle_auth_state")
        if not state:
            return
        cache[state] = {
            "source": app_state.project.source.to_dict(),
            "key": app_state.development_key,
        }

    oauth_state = authentication.get_state_from_session_args()
    if oauth_state and oauth_state in cache:
        state.project.source.param.update(**cache[oauth_state]["source"])
        state._set_development(cache[oauth_state]["key"])  # pylint: disable=protected-access

    template = pn.template.FastGridTemplate(
        site=state.site.name,
        title=state.site.title,
        theme_toggle=False,
        prevent_collision=True,
        save_layout=True,
        site_url="https://awesome-panel.org",
        favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",  # pylint: disable=line-too-long
        sidebar=[
            getting_started,
            share_project,
            authentication,
            gallery,
            project_builder.jsactions,
        ],
    )
    template.main[0:5, 0:6] = source_pane
    template.main[0:5, 6:12] = target_pane
    logger.info("CREATE FINISHED")
    return template


if __name__ == "__main__":
    from panel_sharing.utils import Timer

    with Timer(name="First"):
        create()
    with Timer(name="Second"):
        create()
    with Timer(name="Third"):
        create()
