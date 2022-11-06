import numpy as np
from bokeh.layouts import row
from bokeh.models import Column, ColumnDataSource
from bokeh.models.widgets import Slider
from bokeh.plotting import figure

# Set up data
N = 200
x = np.linspace(0, 4 * np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))


# Set up plot
plot = figure(
    plot_height=400,
    title="my sine wave",
    tools="crosshair,pan,reset,save,wheel_zoom",
    x_range=[0, 4 * np.pi],
    y_range=[-2.5, 2.5],
)

plot.line("x", "y", source=source, line_width=3, line_alpha=0.6)
plot.title.text = "My sine wave"


# Set up widgets
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0)
phase = Slider(title="phase", value=0.0, start=0.0, end=2 * np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1)


# Set up callbacks
def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    x = np.linspace(0, 4 * np.pi, N)
    y = a * np.sin(k * x + w) + b

    source.data = dict(x=x, y=y)


for w in [offset, amplitude, phase, freq]:
    w.on_change("value", update_data)


# Set up layouts and add to document
inputs = Column(offset, amplitude, phase, freq, sizing_mode="fixed")

bokeh_component = row(inputs, plot, sizing_mode="stretch_width")

# Set up Panel

import panel as pn

pn.extension(template="fast")
pn.panel(bokeh_component).servable()

pn.state.template.param.update(
    site="Awesome Panel",
    site_url="https://awesome-panel.org",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
    title="Bokeh App",
)
