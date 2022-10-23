import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")
pn.state.template.param.update(
    site="Panel Sharing",
    title="Welcome",
    site_url="https://awesome-panel.org",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
)

pn.panel(
    """# Welcome to Panel Sharing! ❤️

Panel is an open-source data app Python library that supports your workflow from data exploration to
production. Panel is very popular in *real* science, engineering and finance. It can be used successfully in
any domain.

Here you can develop, [convert](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html) and share Panel apps. NO SERVER REQUIRED.

**Select an example app in the sidebar** to get started.

## About

This project was made with Panel! Check out the code and **report issues at
[github/awesome-panel/panel-sharing](https://github.com/awesome-panel/panel-sharing)**.

## Resources

- [Panel](https://panel.holoviz.org) | [WebAssembly User Guide](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html) | [Community Forum](https://discourse.holoviz.org/) | [Github Code](https://github.com/holoviz/panel) | [Github Issues](https://github.com/holoviz/panel/issues) | [Twitter](https://mobile.twitter.com/panel_org) | [LinkedIn](https://www.linkedin.com/company/79754450)
- [Awesome Panel](https://awesome-panel.org) | [Github Code](https://github.com/marcskovmadsen/awesome-panel) | [Github Issues](https://github.com/MarcSkovMadsen/awesome-panel/issues)
- Marc Skov Madsen | [Twitter](https://twitter.com/MarcSkovMadsen) | [LinkedIn](https://www.linkedin.com/in/marcskovmadsen/)
- Sophia Yang | [Twitter](https://twitter.com/sophiamyang) | [Medium](https://sophiamyang.medium.com/)
- [Pyodide](https://pyodide.org) | [FAQ](https://pyodide.org/en/stable/usage/faq.html)
- [PyScript](https://pyscript.net/) | [FAQ](https://docs.pyscript.net/latest/reference/faq.html)
"""
).servable()
