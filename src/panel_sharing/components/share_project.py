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

By clicking the *share* button, I make my code **open source, free and MIT licensed**.
"""


class ShareProject(pn.viewable.Viewer):
    app_state = param.ClassSelector(class_=AppState)
    js_actions = param.ClassSelector(class_=JSActions)

    share = param.Event()
    shared_url = param.String()

    open_shared_link = param.Event()
    copy_shared_link = param.Event()

    reset = param.Action()

    def __init__(self, app_state: AppState, js_actions: JSActions):
        super().__init__(app_state=app_state, js_actions=js_actions)
        self.reset = self._reset
        self.share_button = pn.widgets.Button.from_param(
            self.param.share,
            name="❤️ Share",
            sizing_mode="stretch_width",
            align="end",
            button_type="success",
        )
        self.project = pn.widgets.TextInput.from_param(
            self.app_state.project.param.name, name="Project"
        )
        self.open_shared_link_button = pn.widgets.Button.from_param(
            self.param.open_shared_link,
            name="🔗 OPEN",
            sizing_mode="stretch_width",
            align="end",
            button_type="light",
        )
        self.copy_shared_link_button = pn.widgets.Button.from_param(
            self.param.copy_shared_link,
            name="✂️ COPY",
            sizing_mode="stretch_width",
            align="end",
            button_type="light",
        )

    @pn.depends("share", watch=True)
    def _share(self):
        self.shared_url = self.app_state.share()
        if pn.state.notifications:
            pn.state.notifications.success("Release succeeded")

    @pn.depends("open_shared_link", watch=True)
    def _open_shared_link(self):
        self.js_actions.open(url=self.shared_url)

    @pn.depends("copy_shared_link", watch=True)
    def _copy_shared_link(self):
        self.js_actions.copy(url=self.shared_url)

    @pn.depends("app_state.user.authenticated", "shared_url")
    def _panel(self):
        if not self.app_state.user.authenticated:
            return pn.Column(LOGIN_TEXT)
        if not self.shared_url:
            return pn.Column(LICENSE_TEXT, self.project, self.share_button)
        return pn.Column(
            LICENSE_TEXT,
            self.project,
            self.share_button,
            self.copy_shared_link_button,
            self.open_shared_link_button,
            sizing_mode="stretch_width",
        )

    @pn.depends("share", watch=True)
    def _handle_sharing(self):
        self.shared = True

    def __panel__(self):
        return pn.panel(self._panel)

    def _reset(self, _):
        self.shared_url = ""


if __name__.startswith("bokeh"):
    pn.extension(notifications=True, template="fast")
    js_actions = JSActions()
    app = AppState()
    app.user.param.authenticated.constant = False
    share = ShareProject(app_state=app, js_actions=js_actions)

    pn.Column(app.user.param.authenticated, share.param.reset, js_actions).servable()
    share.servable(target="sidebar")
