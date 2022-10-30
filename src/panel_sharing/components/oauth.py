"""The OAuth component enables users to authenticate with Github"""
from __future__ import annotations

import json
import logging
import os
import urllib.parse as urlparse
import uuid

import panel as pn
import param
import requests
from tornado.web import create_signed_value, decode_signed_value

logger = logging.getLogger()


class JSActions(pn.reactive.ReactiveHTML):  # pylint: disable=too-many-ancestors
    """Helper class for triggering js functions"""

    # .event cannot trigger on js side. Thus I use Integer
    _url = param.String()
    _open = param.Boolean()

    _set_cookie = param.Dict()
    _delete_secure_cookie = param.String()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        "_open": "window.open(data._url, '_self')",
        "_set_cookie": """
function createCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/;secure";
}      
const {name, value, days}=data._set_cookie
createCookie(name, value, days)""",
        "_delete_secure_cookie": """
value=data._delete_secure_cookie+'=; Max-Age=-99999999; path=/;secure'
document.cookie = value""",
    }

    def __init__(self):
        super().__init__(height=0, width=0, sizing_mode="fixed", margin=0)

    def open(self, url: str):
        """Opens the url in a new tab"""
        if url:
            self._url = url
            self._open = not self._open
        else:
            raise ValueError("No url to open")

    def set_secure_cookie(self, name, value, days=1.0):
        """Sets a cookie as a secure cookie

        Args:
            name: The name of the cookie
            value: The value of the cookie. Please not you will have to encrypt this your self
            days: Days to expiration. Defaults to 1.0.
        """
        self._set_cookie = {"name": name, "value": value, "days": days}

    def delete_secure_cookie(self, name):
        """Deletes the cookie

        Args:
            name: The name of the cookie to delete
        """
        self._delete_secure_cookie = name


class OAuth(pn.viewable.Viewer):
    """Enables users to authenticate with Github

    To use it please create an oauth app as described in
    https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app

    Then follow the description in https://panel.holoviz.org/user_guide/Authentication.html and

    - Set the ENVIRONMENT VARIABLES
      - `PANEL_OAUTH_KEY`
      - `PANEL_OAUTH_SECRET`
      - `PANEL_OAUTH_REDIRECT_URI` (optional)
    - Create a Cookie Secret via `panel secret` and set the environment variable
      - `PANEL_COOKIE_SECRET`
    """

    log_in = param.Event(label="Log in via Github")
    log_out = param.Event(
        label="Log out",
    )

    user_info = param.Dict(constant=True)
    user = param.String(constant=True)
    access_token = param.String(constant=True)

    state = param.String(constant=True)

    def __init__(self, **params):
        params["user_info"] = params.get("user_info", {})
        params["user"] = params.get("user", "")
        params["access_token"] = params.get("access_token", "")

        super().__init__(**params)

        self._client_id = os.environ.get("PANEL_OAUTH_KEY", "")
        self._client_secret = os.environ.get("PANEL_OAUTH_SECRET", "")
        self._cookie_secret = os.environ.get("PANEL_COOKIE_SECRET", "")
        self._oauth_redirect_uri = os.environ.get("PANEL_OAUTH_REDIRECT_URI", "")
        self._jsactions = JSActions()

        self._set_user_from_cookie()
        if not self.user:
            self._set_user_from_redirect()

    @pn.depends("user")
    def _panel(self):
        if not self.configured:
            return pn.pane.Alert("Auth is not configured", alert_type="danger")
        if self.user:
            return pn.Column(
                self._jsactions,
                self.param.log_out,
                # pn.widgets.TextInput.from_param(self.param.user),
            )
        return pn.Column(
            self._jsactions, pn.widgets.Button.from_param(self.param.log_in, button_type="default")
        )

    @property
    def configured(self) -> bool:
        """Returns True if the component has been configured, i.e. the relevant environment
        variables have been set"""
        return all(
            (self._client_id, self._client_secret, self._cookie_secret, self._oauth_redirect_uri)
        )

    def __panel__(self):
        return pn.panel(self._panel)

    def _set_user_from_cookie(self):
        user_info = self._get_secure_cookie("user_info")
        if user_info:
            if "login" in user_info:
                with param.edit_constant(self):
                    self.user_info = json.loads(user_info)
                    self.user = self.user_info["login"]
                    print("login")

    def _set_secure_cookie(self, name, value, days=10):
        signed_value = create_signed_value(self._cookie_secret, name, value).decode("utf8")
        self._jsactions.set_secure_cookie(name=name, value=signed_value, days=days)

    def _get_secure_cookie(self, name: str) -> str | None:
        signed_value = pn.state.cookies.get(name, "")
        value = decode_signed_value(secret=self._cookie_secret, name=name, value=signed_value)
        if value:
            return value.decode(encoding="utf8")
        return ""

    def _delete_secure_cookie(self, name: str):
        self._jsactions.delete_secure_cookie(name)

    def _is_valid(self, state: str) -> bool:
        return bool(self._get_secure_cookie("state") == state and state)

    def _create_state(self):
        with param.edit_constant(self):
            self.state = str(uuid.uuid4())
        self._set_secure_cookie("state", self.state, days=1.0 / 24 / 60 / 6)

        return self.state

    @pn.depends("log_in", watch=True)
    def _log_in_handler(self, _=None):
        url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={self._client_id}"
            f"&state={self._create_state()}"
            f"&allow_signup=true"
        )
        self._jsactions.open(url)

    @pn.depends("log_out", watch=True)
    def _log_out_handler(self):
        self._delete_secure_cookie("user_info")
        self._delete_secure_cookie("access_token")
        with param.edit_constant(self):
            self.user_info = {}
            self.user = ""
            self.access_token = ""
            self.param.trigger("user")

    def _set_user_from_redirect(self):
        code = pn.state.session_args.get("code", [b""])[0].decode("utf8")
        with param.edit_constant(self):
            self.state = pn.state.session_args.get("state", [b""])[0].decode("utf8")
        if self._is_valid(state=self.state) and code:
            access_token = self._get_access_token(code)
            if access_token:
                self._set_user_from_access_token(access_token)
        with param.edit_constant(self):
            self.state = ""

    def _set_user_from_access_token(self, access_token):
        response = requests.get(
            url="https://api.github.com/user",
            timeout=20,
            headers=dict(
                authorization=f"Bearer {access_token}",
                accept="application/json",
            ),
        )
        response_json = response.json()
        if "login" in response_json:
            with param.edit_constant(self):
                self.user_info = response_json
                self.user = self.user_info["login"]
                self.access_token = access_token

                def on_load():
                    self._set_secure_cookie("access_token", self.access_token, days=10)
                    self._set_secure_cookie(name="user_info", value=json.dumps(self.user_info))
                    self._delete_secure_cookie("state")
                    if pn.state.location:
                        query = pn.state.location.query_params
                        if "code" in query:
                            del query["code"]
                        if "state" in query:
                            del query["state"]
                        pn.state.location.search = "?" + urlparse.urlencode(query)

                pn.state.onload(on_load)
            print(f"{self.user_info['html_url']} logged in successfully")

    def _get_access_token(self, code: str):
        if not code:
            return ""

        response = requests.post(
            url="https://github.com/login/oauth/access_token",
            timeout=20,
            headers=dict(
                accept="application/json",
            ),
            data=dict(
                redirect_uri=self._oauth_redirect_uri,
                client_id=self._client_id,
                client_secret=self._client_secret,
                code=code,
            ),
        )
        if not "access_token" in response.json():
            return ""
        return response.json()["access_token"]


if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")

    component = OAuth()

    pn.Column(
        component,
        pn.bind(pn.pane.JSON, object=component.param.user_info),
    ).servable()
