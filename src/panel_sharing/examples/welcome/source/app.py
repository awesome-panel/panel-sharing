import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")

pn.Column(
    pn.panel(
        """# Welcome to Panel Sharing ❤️

[Panel](https://panel.holoviz.org) is an open-source, data app framework that supports your workflow from exploration to
production. Panel is very popular in *real* science, engineering and finance. It can be used successfully in
any domain.

[Panel sharing](https://github.com/awesome-panel/panel-sharing) is **the fastest way to develop, [convert](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html) and share Panel data apps**.

Panel Sharing was made with Panel! Check out the code and **report issues
[here](https://github.com/awesome-panel/panel-sharing)**.

**Select an example app in the sidebar** to get started.
"""
    ),
    pn.pane.Alert(
        "Panel Sharing is **currently a prototype**. **Your code and apps will not be persisted!**",
        alert_type="danger",
        margin=(0, 10),
    ),
).servable()

pn.state.template.param.update(
    site="Panel Sharing",
    title="Welcome",
    site_url="https://github.com/awesome-panel/panel-sharing",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
)
