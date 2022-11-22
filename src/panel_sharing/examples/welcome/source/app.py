import panel as pn

pn.extension(sizing_mode="stretch_both")

pn.Column(
    pn.pane.Markdown(
        """# Welcome to Panel Sharing ❤️

[Panel sharing](https://github.com/awesome-panel/panel-sharing) is the fastest way to share data apps with the world.

Check out the [User Guide](https://github.com/awesome-panel/panel-sharing/blob/main/docs/user-guide.md) and report issues
at [panel-sharing](https://github.com/awesome-panel/panel-sharing).

<video width="100%" height="400" controls autoplay>
    <source src="https://sharing.awesome-panel.org/awesome-panel-sharing.mp4" type="video/mp4" />
</video><br>"""
    ),
).servable()
