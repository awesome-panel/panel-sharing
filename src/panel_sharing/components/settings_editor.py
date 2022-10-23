"""The settings_editor enables a user to edit some of the app settings"""
import panel as pn


def settings_editor(state):
    """The settings_editor enables a user to edit some of the app settings"""
    return pn.Column(
        pn.widgets.TextInput.from_param(state.user.param.name, name="User"),
        pn.widgets.TextInput.from_param(state.project.param.name, name="Project"),
        pn.widgets.TextInput.from_param(state.param.shared_url, name="Url", disabled=True),
        pn.widgets.Button(name="🗑️ DELETE", disabled=True),
        name="Configure",
        sizing_mode="stretch_both",
    )
