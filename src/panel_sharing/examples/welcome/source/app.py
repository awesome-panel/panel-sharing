import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")
pn.state.template.param.update(site="Panel Sharing", title="Welcome")

pn.panel("""# Welcome to Panel Sharing! ❤️

Panel is an open-source data app Python library that supports your workflow from data exploration to
production. Panel is very popular in *real* science, engineering and finance. It can be used in
any domain.

Here you can develop and convert Panel apps to webassembly.
When you are done, you can share them with the world. NO SERVER REQUIRED.

**Select an example app in the sidebar** to get started.""").servable()