"""The OAuth component enables users to authenticate with Github"""
from __future__ import annotations

import logging
import os
import uuid

import panel as pn
import param
import requests
from diskcache import Cache
from tornado.web import create_signed_value, decode_signed_value

from panel_sharing.utils import del_query_params

cache = Cache(".cache/panel_sharing_oauth")

logger = logging.getLogger("oauth")
logger.setLevel(logging.INFO)

SECURE_COOKIE = "state"
SECURE_COOKIE_TTL_IN_DAYS = 10


class JSActions(pn.reactive.ReactiveHTML):  # pylint: disable=too-many-ancestors
    """Helper class for triggering js functions"""

    # .event cannot trigger on js side. Thus I use Integer
    _url = param.String()
    _open = param.Boolean()

    _set_cookie = param.Dict()
    _delete_secure_cookie = param.String()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        "_open": "console.log(data._url);window.open(data._url, '_self')",
        "_set_cookie": """
console.log("set cookie")
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
createCookie(name, value, days)
console.log("cookie set")""",
        "_delete_secure_cookie": """
console.log("delete cookie")
value=data._delete_secure_cookie+'=; Max-Age=-99999999; path=/;secure'
document.cookie = value
console.log("cookie deleted")
""",
    }

    def __init__(self):
        super().__init__(height=0, width=0, sizing_mode="fixed", margin=0)

    def open(self, url: str):
        """Opens the url in the same tab"""
        logger.info("Open and redirect to %s", url)
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
        logger.info("set_secure_cookie %s %s", name, value)
        self._set_cookie = {"name": name, "value": value, "days": days}

    def delete_secure_cookie(self, name):
        """Deletes the cookie

        Args:
            name: The name of the cookie to delete
        """
        logger.info("delete_secure_cookie %s", name)
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

    state = param.String()

    def __init__(self):
        super().__init__()

        self._client_id = os.environ.get("PANEL_OAUTH_KEY", "")
        self._client_secret = os.environ.get("PANEL_OAUTH_SECRET", "")
        self._cookie_secret = os.environ.get("PANEL_COOKIE_SECRET", "")
        self._oauth_redirect_uri = os.environ.get("PANEL_OAUTH_REDIRECT_URI", "")
        self._jsactions = JSActions()

        self._set_user_from_state()
        if not self.user:
            self._set_user_from_redirect()

        pn.state.onload(lambda: del_query_params("code", "state", period=1000))

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

    def _set_user_from_state(self):
        state = self._get_secure_cookie(SECURE_COOKIE)
        user_info = cache.get(state, {}).get("user_info", {})
        user = user_info.get("login", "")
        if user_info and user:
            with param.edit_constant(self):
                self.user_info = user_info
                self.user = user
                logger.info("Logged in user %s from user_info in state", self.user)
        else:
            logger.info("No user_info in state.")

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
        cookie_state = self._get_secure_cookie("state")
        logger.info("expected state %s", state)
        logger.info("cookie   state %s", cookie_state)
        return bool(state and cookie_state == state)

    def _create_state(self):
        with param.edit_constant(self):
            self.state = str(uuid.uuid4())
        self._set_secure_cookie(SECURE_COOKIE, self.state, days=SECURE_COOKIE_TTL_IN_DAYS)
        cache[self.state] = {}
        return self.state

    @pn.depends("log_in", watch=True)
    def _log_in_handler(self, _=None):
        logger.info("Login triggered. Redirecting to https://github.com/login/oauth/authorize")
        url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={self._client_id}"
            f"&state={self._create_state()}"
            f"&allow_signup=true"
        )
        self._jsactions.open(url)

    @pn.depends("log_out", watch=True)
    def _log_out_handler(self):
        user = self.user
        state = self._get_secure_cookie(SECURE_COOKIE)
        self._delete_secure_cookie(SECURE_COOKIE)
        del cache[state]

        with param.edit_constant(self):
            self.user_info = {}
            self.user = ""
            self.param.trigger("user")
        logger.info("Logged out %s", user)

    def _set_user_from_redirect(self):
        code = self._get_code_from_session_args()
        if not code:
            logger.info("No code found in session_args")
            return
        logger.info("Code %s found in session_args", code)

        state = self.get_state_from_session_args()
        if not state:
            logger.info("No state found in session_args")
            return
        logger.info("State %s found in session_args", state)

        if self._is_valid(state=state):
            logger.info("State is valid")
            access_token = self._request_access_token(code)
            if access_token:
                logger.info("access_token received")
                user_info = self._request_user_info(access_token=access_token)
                if user_info:
                    logger.info("user_info received")
                    self._set_user(user_info, state=state)
                else:
                    logger.info("No user_info received")
            else:
                logger.info("No access_token received")
        else:
            logger.info("state is not valid")

    def _set_user(self, user_info, state):
        with param.edit_constant(self):
            self.user_info = user_info
            self.user = self.user_info["login"]
            cache[state] = {"user_info": self.user_info}

        logger.info("Logged in %s successfully", self.user)

    def _get_code_from_session_args(self):
        return pn.state.session_args.get("code", [b""])[0].decode("utf8")

    def get_state_from_session_args(self):
        """Returns the state value or '' if not given"""
        return pn.state.session_args.get("state", [b""])[0].decode("utf8")

    def _request_user_info(self, access_token: str):
        response_json = requests.get(
            url="https://api.github.com/user",
            timeout=20,
            headers=dict(
                authorization=f"Bearer {access_token}",
                accept="application/json",
            ),
        ).json()
        if "login" in response_json:
            return response_json
        print(response_json)
        return {}

    def _request_access_token(self, code: str):
        if not code:
            return ""

        access_token_json = requests.post(
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
        ).json()
        if not "access_token" in access_token_json:
            return ""
        return access_token_json["access_token"]


if __name__.startswith("bokeh"):
    print("RESTARTING")

    pn.extension(sizing_mode="stretch_width")

    component = OAuth()

    pn.Column(
        component,
        pn.bind(pn.pane.JSON, object=component.param.user_info),
    ).servable()
