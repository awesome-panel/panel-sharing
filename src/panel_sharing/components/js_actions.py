import panel as pn
import param


class JSActions(pn.reactive.ReactiveHTML):
    # .event cannot trigger on js side. Thus I use Integer
    _url = param.String()
    _open = param.Boolean()
    _copy = param.Boolean()

    _template = """<div id="jsaction" style="height:0px;width:0px"></div>"""
    _scripts = {
        # Todo: Make this more robust by removing fragile replace
        "_open": "url=window.location.href.substring(0, location.href.lastIndexOf('/')+1) +  data._url;window.open(url, '_blank')",
        "_copy": "url=window.location.href.substring(0, location.href.lastIndexOf('/')+1) +  data._url;navigator.clipboard.writeText(url)",
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

    def copy(self, url: str):
        """Copies the url to the clipboard"""
        if url:
            self._url = url
            self._copy = not self._copy
        else:
            raise ValueError("No url to copy")
