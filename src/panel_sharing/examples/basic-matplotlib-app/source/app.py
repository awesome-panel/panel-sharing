import numpy as np
import panel as pn
from matplotlib.figure import Figure

pn.extension(sizing_mode="stretch_width", template="fast")


@pn.cache()
def plot_output(bins=10) -> Figure:
    fig0 = Figure(figsize=(12, 6))
    ax0 = fig0.subplots()

    np.random.seed(19680801)
    x = 100 + 15 * np.random.randn(437)
    ax0.hist(x, bins, density=True)

    return fig0


bins_input = pn.widgets.IntSlider(name="bins", value=20, start=20, end=200, step=20)
plot_output = pn.bind(plot_output, bins=bins_input)

pn.Column(
    bins_input,
    pn.panel(plot_output, height=400, sizing_mode="stretch_both", align="center"),
    sizing_mode="stretch_both",
).servable()

pn.state.template.param.update(
    site="Awesome Panel Sharing",
    site_url="https://awesome-panel.org/sharing",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
    title="Bokeh Matplotlib App",
)
