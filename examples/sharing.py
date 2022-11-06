from panel_sharing import sharing

if __name__.startswith("bokeh"):
    import mimetypes
    mimetypes.add_type("application/javascript", ".js")
    sharing.create().servable()