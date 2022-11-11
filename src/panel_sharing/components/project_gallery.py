"""The Gallery component enables users to select a project from a list of projects"""
import random
from typing import List

import panel as pn

from panel_sharing import config
from panel_sharing.models import AzureBlobStorage
from panel_sharing.utils import Timer

RAW_CSS = """
.cards-grid {
  --cards-grid-min-size: 16rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--cards-grid-min-size), 1fr));
  grid-gap: 2rem;
  list-style: none;
}
/* Style the counter cards */
.card {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  padding: 16px;
  text-align: center;
  background-color: #f1f1f1;
}
/* Presentational styles */
.card {
  padding: 0px;
}

.cards-grid {
    margin: 2rem;
    padding: 0px;
}

.avatar {
    vertical-align: middle;
    float: right;
    width: 30px;
    height: 30px;
    margin-top: 5px;
    margin-bottom: 10px;
    margin-left: 5px;
    border-radius: 50%;
}
.card-actions {
    margin-left: 1em;
    margin-right: 1em;
}
.card-action svg {
    vertical-align: middle;
    float: left;
    height: 20px;
    color: white;
    margin-top: 10px;
    margin-right: 10px;
    fill: var(--neutral-foreground-rest);
}
.card-action.github-action svg {
    color: var(--neutral-foreground-rest);
}
.card-image {
    height: 200px;
    width: 100%;
}
.card-content {
    padding: 10px 10px 10px;
    color: var(--neutral-foreground-rest);
}

*|*:link {
    text-decoration: none;
}

.card-text {
    height: 100px;
}
.card-header {
    height: 2em;
}
"""

SHARING_URL = config.SITE_URL
WEB_URL = config.AZURE_WEB_URL
# pylint: disable=line-too-long
image_urls = [
    "https://media.wired.com/photos/5eaca02f381a11d296a5adab/master/w_1600,c_limit/photo_space_hubble_1_stsci-h-p2016a-m.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Rayleigh-Taylor_instability.jpg/280px-Rayleigh-Taylor_instability.jpg",
    "https://media.wired.com/photos/5a5bbb1be251803428fea2a9/master/pass/hiv-virus-visual-science-company.jpg",
    "https://blog.siggraph.org/wp-content/uploads/2019/07/Art-of-Comm.png",
    "https://www.nvidia.com/content/dam/en-zz/Solutions/high-performance-computing/scientific-visualization/nvidia-vmd-arm-molecular-sim-4c25-p@2x.jpg",
]
# pylint: enable=line-too-long
MAX_CARDS = 50


def _get_card(key: str) -> str:
    """Returns a Fast HTML card"""
    app_author, app_name = key.split("/", 2)
    app_url = f"{WEB_URL}{key}/app.html"
    app_description = f"by {app_author}"
    app_author_url = f"https://github.com/{app_author}"
    app_code = f"sharing?app={key}"
    app_author_avatar = f"https://github.com/{app_author}.png?size=40"

    image_url = random.choice(image_urls)

    return f"""
<li class="card">
<fast-card class="gallery-item">
<a title="Click to open" class="card-action" href="{ app_url }">
<img class="card-image" src="{image_url}"/>
<div class="card-content">
    <h2 class="card-header">{ app_name }</h2>
    <p class="card-text">{ app_description }</p>
</div></a>
<div class="card-actions">
    <a class="card-action author-action" href="{ app_author_url }" target="_blank">
        <img src="{ app_author_avatar }" alt="avatar" class="avatar" title="author: {app_author}">
    </a>
    <a title="Edit the Code" appearance="neutral" class="card-action code-action" href="{app_code}">
        <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" d="M4.854 4.146a.5.5 0 0 1 0 .708L1.707 8l3.147 3.146a.5.5 0 0 1-.708.708l-3.5-3.5a.5.5 0 0 1 0-.708l3.5-3.5a.5.5 0 0 1 .708 0zm6.292 0a.5.5 0 0 0 0 .708L14.293 8l-3.147 3.146a.5.5 0 0 0 .708.708l3.5-3.5a.5.5 0 0 0 0-.708l-3.5-3.5a.5.5 0 0 0-.708 0zm-.999-3.124a.5.5 0 0 1 .33.625l-4 13a.5.5 0 0 1-.955-.294l4-13a.5.5 0 0 1 .625-.33z"/>
        </svg>
    </a>
</div>
</fast-card>
</li>
"""


def _get_content(key: str, apps: List[str]):
    max_apps = False
    content = ""
    filter_apps = []
    for app in sorted(apps):
        if key in app:
            filter_apps.append(app)

    if len(filter_apps) > MAX_CARDS:
        filter_apps = filter_apps[0:MAX_CARDS]
        max_apps = True
    for app in sorted(filter_apps):
        content += _get_card(app)

    content = f"""
    <style>{RAW_CSS}</style>
    <div id="cards">
    <ul class="cards-grid">
    {content}
    </ul>
    </div>
    """

    if max_apps:
        # pylint: disable=line-too-long
        content = (
            f"<p style='margin-left:35px'>Too many apps found. Showing the first {len(filter_apps)} of {len(apps)} apps. "
            "<b>Please make your search more specific</b>.</p>" + content
        )
        # pylint: enable=line-too-long
    return content


@pn.cache(ttl=60)
def _get_keys():
    with Timer(name="get_keys"):
        return AzureBlobStorage().get_keys()


def create_project_gallery():
    """Returns an AppGallery wrapped in a Template"""
    apps = _get_keys()

    container = pn.pane.HTML(sizing_mode="stretch_both")
    key_input = pn.widgets.TextInput(
        name="Search", margin=(0, 0, 0, 35), max_width=500, sizing_mode="stretch_width"
    )

    def get_content(key, apps):
        container.object = _get_content(key, apps)

    get_content("", apps)
    pn.bind(get_content, key=key_input.param.value_input, apps=apps, watch=True)

    return pn.template.FastListTemplate(
        site=config.SITE,
        site_url="https://awesome-panel.org/sharing_gallery",
        title="Panel Sharing Gallery",
        main=[key_input, container],
        main_layout="",
    )


if __name__.startswith("bokeh"):
    create_project_gallery().servable()
