import holoviews as hv
import hvplot.pandas
import panel as pn
from bokeh.sampledata.iris import flowers

pn.extension(sizing_mode="stretch_width")
hv.extension("bokeh")

accent_color = "#ff286e"


def get_plot():
    scatter = flowers.hvplot.scatter(
        x="sepal_length", y="sepal_width", c=accent_color, responsive=True, height=300
    )
    hist = flowers.hvplot.hist("petal_width", c=accent_color, responsive=True, height=300)

    scatter.opts(size=10)

    selection_linker = hv.selection.link_selections.instance()

    scatter = selection_linker(scatter)
    hist = selection_linker(hist)

    scatter.opts(tools=["hover"], active_tools=["box_select"])
    hist.opts(tools=["hover"], active_tools=["box_select"])

    return (scatter + hist).cols(1)


plot = get_plot()

pn.template.FastListTemplate(
    site="Awesome Panel",
    title="Cross Filtering",
    header_background=accent_color,
    main=[plot],
).servable()