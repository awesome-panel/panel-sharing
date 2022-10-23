"""The BuildProject component enables users to convert the project"""
import panel as pn
import param

from panel_sharing.components.js_actions import JSActions


class BuildProject(pn.viewable.Viewer):
    """A component that enables users to convert the project"""

    convert = param.Event()

    open_developer_link = param.Event()

    _state = param.Parameter()
    jsactions = param.ClassSelector(class_=JSActions)

    def __init__(self, state, **params):
        if "jsactions" not in params:
            params["jsactions"] = JSActions()
        super().__init__(_state=state, **params)

        self._panel = self._get_panel()

    def __panel__(self):
        return self._panel

    @pn.depends("convert", watch=True)
    def _convert(self):
        self._state.build()

        if pn.state.notifications:
            pn.state.notifications.success("Build succeeded")

    @pn.depends("open_developer_link", watch=True)
    def _open_developer_link(self):
        self.jsactions.open(url=self._state.development_url)

    def _download_callback(self):
        key = self._state.development_key
        return self._state.site.development_storage.get_zipped_folder(key=key)

    def _get_panel(self):
        self.convert_button = pn.widgets.Button.from_param(
            self.param.convert,
            name="🏃 Convert",
            sizing_mode="stretch_width",
            align="end",
            button_type="primary",
        )
        self.open_developer_link_button = pn.widgets.Button.from_param(
            self.param.open_developer_link,
            name="🔗 OPEN",
            width=125,
            sizing_mode="fixed",
            align="end",
            button_type="light",
        )
        self.download_converted_files = pn.widgets.FileDownload(
            callback=self._download_callback,
            filename="build.zip",
            width=125,
            button_type="light",
            sizing_mode="fixed",
            label="📁 DOWNLOAD",
            align="end",
        )

        return pn.Row(
            self.convert_button,
            # , self.open_developer_link_button, self.download_converted_files,
            # self.share_button, self.open_shared_link_button, self.copy_shared_link_button,
            sizing_mode="stretch_width",
            margin=(0, 5, 10, 5),
        )
