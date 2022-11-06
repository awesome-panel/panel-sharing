import panel as pn

pn.extension(template="fast")

pn.panel("This is a basic Panel app").servable()

pn.state.template.param.update(
    site="Awesome Panel Sharing",
    site_url="https://awesome-panel.org/sharing",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
    title="Basic App",
)