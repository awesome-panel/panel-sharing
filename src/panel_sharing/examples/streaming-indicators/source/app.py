import numpy as np
import panel as pn

pn.extension(sizing_mode="stretch_width")

INDICATORS = 32
PERIOD = 200  # mili seconds

indicators = (
    pn.indicators.Trend(
        data={"x": list(range(10)), "y": np.random.randn(10).cumsum()},
        width=150,
        height=100,
        plot_type=pn.indicators.Trend.param.plot_type.objects[i % 4],
    )
    for i in range(INDICATORS)
)
layout = pn.layout.FlexBox(*indicators)


def stream():
    for trend in layout:
        trend.stream(
            {"x": [trend.data["x"][-1] + 1], "y": [trend.data["y"][-1] + np.random.randn()]},
            rollover=20,
        )


periodic_callback = pn.state.add_periodic_callback(stream, PERIOD)

pn.template.FastListTemplate(
    site="Awesome Panel Sharing",
    site_url="https://awesome-panel.org/sharing",
    favicon="https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel-assets/320297ccb92773da099f6b97d267cc0433b67c23/favicon/ap-1f77b4.ico",
    title="Streaming Indicators",
    main=[
        layout,
    ],
).servable()
