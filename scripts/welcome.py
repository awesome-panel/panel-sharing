import panel as pn

pn.extension(sizing_mode="stretch_both")

pn.Column(
    pn.pane.Markdown(
        """# Welcome to Panel Sharing ❤️

<a href="https://github.com/awesome-panel/panel-sharing" target="_blank">Panel sharing</a> is **the fastest way to share data apps** with the world.

Check out the <a href="https://github.com/awesome-panel/panel-sharing/blob/main/docs/user-guide.md" target="_blank">User Guide</a> and report issues
at <a href="https://github.com/awesome-panel/panel-sharing" target="_blank">panel-sharing</a>.

<video width="100%" height="400" controls autoplay>
    <source src="https://sharing.awesome-panel.org/awesome-panel-sharing.mp4" type="video/mp4" />
</video><br>"""
    ),
).save("src/panel_sharing/examples/welcome/build/app.html")