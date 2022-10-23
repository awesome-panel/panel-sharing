
import panel as pn

pn.extension(template="fast")
pn.state.template.param.update(site="Panel Sharing", title="Basic App")

pn.panel("This is a basic Panel app").servable()        
