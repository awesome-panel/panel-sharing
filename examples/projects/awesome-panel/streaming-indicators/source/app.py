import numpy as np
import panel as pn

pn.extension(sizing_mode="stretch_width")

INDICATORS = 32
PERIOD = 500 # mili seconds

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
    site="Awesome Panel",
    title="Streaming Indicators",
    main=[layout,],
).servable()