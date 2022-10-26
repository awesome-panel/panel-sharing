"""The Authentication enables users to authenticate with Github"""
import panel as pn
import param

from panel_sharing.models import AppState

TEXT = """\
## Authentication"""


class Authentication(pn.viewable.Viewer):
    """An authentication component for Github"""

    login = param.Event()
    logout = param.Event()

    app_state = param.ClassSelector(class_=AppState)

    def __init__(self, app_state: AppState):
        super().__init__(app_state=app_state)

        self.login_button = pn.widgets.Button.from_param(
            self.param.login,
            name="🔓 Log in",
            sizing_mode="stretch_width",
            align="end",
            button_type="success",
        )
        self.logout_button = pn.widgets.Button.from_param(
            self.param.logout,
            name="🔒 Log out",
            sizing_mode="stretch_width",
            align="end",
            button_type="success",
        )

    @pn.depends("app_state.user.authenticated")
    def _panel(self):
        if not self.app_state.user.authenticated:
            return pn.Column(pn.pane.Markdown("## 😺 Authentication"), self.login_button)

        return pn.Column(
            pn.pane.Markdown("## 😺 Authentication"),
            self.app_state.user.param.name,
            self.logout_button,
        )

    @pn.depends("login", watch=True)
    def _login_user(self):
        self.app_state.login()

    @pn.depends("logout", watch=True)
    def _logout_user(self):
        self.app_state.logout()

    def __panel__(self):
        return pn.panel(self._panel)


if __name__.startswith("bokeh"):
    pn.extension(notifications=True, template="fast")
    app = AppState()
    auth = Authentication(app_state=app)

    pn.Column(
        app.user.param.authenticated,
    ).servable()
    auth.servable(target="sidebar")
