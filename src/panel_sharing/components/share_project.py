"""The ShareProject component enables users to share the project"""
import panel as pn
import param

from panel_sharing.components.js_actions import JSActions
from panel_sharing.models import AppState

LOGIN_TEXT = """\
## 🌎 Share

Please login to enable sharing.
"""
LICENSE_TEXT = """\
## 🌎 Share

By clicking the *Share* button, I make my code **open source, free and MIT licensed**.
"""

RAW_CSS = """
#sidebar a.bk-btn.bk-btn-success {
    color: var(--neutral-foreground-rest);
    padding-top: 5px !important;
}
"""


class ShareProject(pn.viewable.Viewer):
    """Enables users to share the project"""

    app_state: AppState = param.ClassSelector(class_=AppState)
    js_actions: JSActions = param.ClassSelector(class_=JSActions)

    share = param.Event()
    shared_url: str = param.String()

    open_shared_link: bool = param.Event()
    copy_shared_link: bool = param.Event()

    reset = param.Action()

    def __init__(self, app_state: AppState, js_actions: JSActions):
        super().__init__(app_state=app_state, js_actions=js_actions)
        self.reset = self._reset
        self.share_button = pn.widgets.Button.from_param(
            self.param.share,
            name="Share",
            sizing_mode="stretch_width",
            align="end",
            button_type="primary",
        )
        self.project = pn.widgets.TextInput.from_param(
            self.app_state.project.param.name, name="Project"
        )
        self.open_shared_link_button = pn.widgets.Button.from_param(
            self.param.open_shared_link,
            name="🔗 Open",
            sizing_mode="stretch_width",
            align="end",
            button_type="success",
        )
        self.copy_shared_link_button = pn.widgets.Button.from_param(
            self.param.copy_shared_link,
            name="✂️ Copy",
            sizing_mode="stretch_width",
            align="end",
            button_type="success",
        )
        self.download_shared_files_button = pn.widgets.FileDownload(
            callback=self._download_callback,
            filename="build.zip",
            button_type="success",
            sizing_mode="stretch_width",
            height=30,
            label="📁 Download",
            align="end",
        )
        if not RAW_CSS in pn.config.raw_css:
            pn.config.raw_css.append(RAW_CSS)

    def _download_callback(self):
        return self.app_state.project.to_zip_folder()

    @pn.depends("share", watch=True)
    def _share(self):
        self.shared_url = self.app_state.share()
        if pn.state.notifications:
            pn.state.notifications.success("Release succeeded")
        if pn.state.location:
            key = self.app_state.shared_key
            pn.state.location.search = ""
            pn.state.location.update_query(app=key)

    @pn.depends("open_shared_link", watch=True)
    def _open_shared_link(self):
        self.js_actions.open(url=self.shared_url)

    @pn.depends("copy_shared_link", watch=True)
    def _copy_shared_link(self):
        self.js_actions.copy(url=self.shared_url)

    @pn.depends("app_state.user.authenticated", "shared_url")
    def _panel(self):
        if not self.app_state.user.authenticated:
            return pn.Column(pn.pane.Markdown(LOGIN_TEXT, margin=0))
        if not self.shared_url:
            return pn.Column(
                pn.pane.Markdown(LICENSE_TEXT, margin=0),
                pn.widgets.TextInput.from_param(self.app_state.user.param.name, name="User"),
                self.project,
                self.share_button,
            )
        return pn.Column(
            pn.pane.Markdown(LICENSE_TEXT, margin=0),
            pn.widgets.TextInput.from_param(self.app_state.user.param.name, name="User"),
            self.project,
            self.share_button,
            self.copy_shared_link_button,
            self.open_shared_link_button,
            self.download_shared_files_button,
            sizing_mode="stretch_width",
        )

    def __panel__(self):
        return pn.panel(self._panel)

    def _reset(self, _):
        self.shared_url = ""


if __name__.startswith("bokeh"):
    pn.extension(notifications=True, template="fast")
    js_actions_ = JSActions()
    app = AppState()
    app.user.param.authenticated.constant = False
    share = ShareProject(app_state=app, js_actions=js_actions_)

    pn.Column(app.user.param.authenticated, share.param.reset, js_actions_).servable()
    share.servable(target="sidebar")
