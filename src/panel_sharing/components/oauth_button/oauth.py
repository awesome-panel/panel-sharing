"""The OAuth component enables users to authenticate with Github"""
import datetime as dt
import os
import uuid

import panel as pn
import param
import requests


class JSActions(pn.reactive.ReactiveHTML):  # pylint: disable=too-many-ancestors
    """Helper class to enable trigger js functions"""

    # .event cannot trigger on js side. Thus I use Integer
    _url = param.String()
    _open = param.Boolean()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        "_open": "console.log(data._url);window.open(data._url, '_self')",
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


class OAuth(param.Parameterized):
    """Enables users to authenticate with Github"""

    authorize = param.Event()

    def __init__(self, **params):
        super().__init__(**params)

        if not "oauth-state" in pn.state.cache:
            pn.state.cache["oauth-state"] = {}

        self._states = pn.state.cache["oauth-state"]
        self._client_id = os.environ["PANEL_OAUTH_KEY"]
        self._client_secret = os.environ["PANEL_OAUTH_SECRET"]
        self.jsactions = JSActions()

        self._is_valid_redirect()

        # https://github.com/login/oauth/access_token

    def _create_state(self):
        state = str(uuid.uuid4())
        value = {
            "expiry": dt.datetime.now() + dt.timedelta(minutes=10),
            "source_url": pn.state.location.href,
        }
        self._states[state] = value
        return state

    def _is_valid(self, state: str) -> bool:
        if state in self._states:
            expiry = self._states[state]["expiry"]
            if dt.datetime.now() < expiry:
                return True
        return False

    @pn.depends("authorize", watch=True)
    def _authorize(self, _=None):
        url = (
            "https://github.com/login/oauth/authorize"
            # f"?redirect_uri={pn.state.location.href}"
            f"?client_id={self._client_id}"
            # "&scope=photos",
            f"&state={self._create_state()}"
            f"&allow_signup=true"
        )
        self.jsactions.open(url)

    def _is_valid_redirect(self):
        code = pn.state.session_args.get("code", [b""])[0].decode("utf8")
        state = pn.state.session_args.get("state", [b""])[0].decode("utf8")
        if self._is_valid(state=state):
            self._get_access_token(code)
        else:
            print("don't redirect")

    def _get_access_token(self, code: str):
        # https://requests.readthedocs.io/en/latest/user/quickstart/
        if not pn.state.location:
            raise NotImplementedError()

        return requests.post(
            url="https://github.com/login/oauth/access_token",
            timeout=20,
            data=dict(
                Accept="application/json",
                redirect_uri=pn.state.location.href,
                client_id=self._client_id,
                client_secret=self._client_secret,
                code=code,
            ),
        )


if __name__.startswith("bokeh"):
    oauth = OAuth()
    pn.Column(oauth.param.authorize, oauth.jsactions, pn.state.location).servable()
