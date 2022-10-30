import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")

pn.panel(
    """# Welcome to Panel Sharing ❤️

Panel is an open-source, data app framework that supports your workflow from exploration to
production. Panel is very popular in *real* science, engineering and finance. It can be used successfully in
any domain.

Here you can develop, [convert](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html) and share Panel apps. NO SERVER REQUIRED.

**Select an example app in the sidebar** to get started.

Panel Sharing was made with Panel! Check out the code and **report issues at
[github/awesome-panel/panel-sharing](https://github.com/awesome-panel/panel-sharing)**.
"""
).servable()

pn.state.template.param.update(
    site="Panel Sharing",
    title="Welcome",
    site_url="https://github.com/awesome-panel/panel-sharing",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
)
