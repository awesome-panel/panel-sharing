"""Default values and other configuration values"""
import os

SITE = "Awesome Panel"
SITE_URL = "https://awesome-panel.org/sharing"
TITLE = "Panel Sharing Alpha"

FAQ = """
# Frequently Asked Questions

## How do I add more files to a project?

You cannot do this as that would complicate this free and personal project.

What you can do is 

- Package your python code into a python package that you share on pypi and add it to the
`requirements`
- Store your other files somewhere public. For example on Github.

## What are the most useful resources for Panel data apps?

- [Panel](https://panel.holoviz.org) | [WebAssembly User Guide](https://panel.holoviz.org/user_guide/Running_in_Webassembly.html) | [Community Forum](https://discourse.holoviz.org/) | [Github Code](https://github.com/holoviz/panel) | [Github Issues](https://github.com/holoviz/panel/issues) | [Twitter](https://mobile.twitter.com/panel_org) | [LinkedIn](https://www.linkedin.com/company/79754450)
- [Awesome Panel](https://awesome-panel.org) | [Github Code](https://github.com/marcskovmadsen/awesome-panel) | [Github Issues](https://github.com/MarcSkovMadsen/awesome-panel/issues)
- Marc Skov Madsen | [Twitter](https://twitter.com/MarcSkovMadsen) | [LinkedIn](https://www.linkedin.com/in/marcskovmadsen/)
- Sophia Yang | [Twitter](https://twitter.com/sophiamyang) | [Medium](https://sophiamyang.medium.com/)
- [Pyodide](https://pyodide.org) | [FAQ](https://pyodide.org/en/stable/usage/faq.html)
- [PyScript](https://pyscript.net/) | [FAQ](https://docs.pyscript.net/latest/reference/faq.html)

"""

ABOUT = """
# About

The purpose of this project is to make it easy for everyone to
build and share Panel data apps.

By using this project you consent to making your project publicly available and
[MIT licensed](https://opensource.org/licenses/MIT).

On the other hand I cannot guarentee the persisting of your project. Use at your own risk.

This project was made with Panel! Check out the code on
[Github](https://github.com/marcskovmadsen/awesome-panel).

Awesome Panel Sharing can also be deployed as a secure solution for your organisation.
If this is something for you contact me via [LinkedIn](https://www.linkedin.com/in/marcskovmadsen).
"""

CODE = """\
import panel as pn

pn.extension(template="fast")
pn.state.template.param.update(site="Panel Sharing", title="Basic App")

pn.panel("This is a basic Panel app").servable()
"""

REQUIREMENTS = ""

HELLO_WORLD_CODE = '''\
import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")
pn.state.template.param.update(site="Panel Sharing", title="Welcome")

pn.panel("""# Welcome to my world! ❤️

Panel is an open-source data app Python library that supports your workflow from data exploration to
production. Panel is very popular in *real* science, engineering and finance. It can be used in
any domain.

Select an example app in the sidebar to get started.

## Resources

- [Panel](https://panel.holoviz.org) | [Github](https://github.com/holoviz/panel) | [Discourse](https://discourse.holoviz.org/)
- [Awesome Panel](https://awesome-panel.org) | [Github](https://github.com/awesome-panel/awesome-panel)

- [Panel](https://holoviz.panel.org) | [WebAssembly User Guide](https://pyviz-dev.github.io/panel/user_guide/Running_in_Webassembly.html) | [Community Forum](https://discourse.holoviz.org/) | [Github Code](https://github.com/holoviz/panel) | [Github Issues](https://github.com/holoviz/panel/issues) | [Twitter](https://mobile.twitter.com/panel_org) | [LinkedIn](https://www.linkedin.com/company/79754450)
- [Awesome Panel](https://awesome-panel.org) | [Github Code](https://github.com/marcskovmadsen/awesome-panel) | [Github Issues](https://github.com/MarcSkovMadsen/awesome-panel/issues)
- Marc Skov Madsen | [Twitter](https://twitter.com/MarcSkovMadsen) | [LinkedIn](https://www.linkedin.com/in/marcskovmadsen/)
- Sophia Yang | [Twitter](https://twitter.com/sophiamyang) | [Medium](https://sophiamyang.medium.com/)
- [Pyodide](https://pyodide.org) | [FAQ](https://pyodide.org/en/stable/usage/faq.html)
- [PyScript](https://pyscript.net/) | [FAQ](https://docs.pyscript.net/latest/reference/faq.html)
""").servable()'''

README = """\
# Introduction

The purpose of this project ...
"""

GUEST_USER_NAME = "guest"
USER_NAME_REGEX = "^[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*$"
PROJECT_NAME = "new"
REPOSITORY_NAME = "new"
AZURE_BLOB_URL = "https://awesomepanelsharing.blob.core.windows.net/"
# "https://awesomepanelsharing.z16.web.core.windows.net/"
AZURE_WEB_URL = "https://sharing.awesome-panel.org/"
AZURE_PROJECT_CONTAINER_NAME = "project"
AZURE_WEB_CONTAINER_NAME = "$web"
AZURE_BLOB_CONN_STR = os.getenv("AZURE_BLOB_CONN_STR", "")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
AZURE_RESOURCE_GROUP_NAME = "awesome-panel"
AZURE_CDN_PROFILE_NAME = "awesome-panel"
AZURE_CDN_ENDPOINT_NAME = "awesome-panel-sharing"
AZURE_APP_CLIENT_ID = os.getenv("AZURE_APP_CLIENT_ID", "")
AZURE_APP_CLIENT_SECRET = os.getenv("AZURE_APP_CLIENT_SECRET", "")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")

AUTHENTICATED = False

SHARING_ENDPOINT = "sharing"
# pylint: disable=line-too-long
THUMBNAIL = """data:image/png;base64,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IDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAADJCT8AAIDkhB8AAEBywg8AACA54QcAAJCc8AMAAEhO+AEAACQn/AAAAJITfgAAAMkJPwAAgOSEHwAAQHLCDwAAIDnhBwAAkJzwAwAASE74AQAAJCf8AAAAkhN+AAAAyQk/AACA5IQfAABAcsIPAAAgOeEHAACQnPADAABITvgBAAAkJ/wAAACSE34AAACpRfx/59g1bsDfGW0AAAAASUVORK5CYII="""
# pylint: enable=line-too-long
