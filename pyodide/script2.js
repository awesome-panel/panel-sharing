importScripts("https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.0/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.0/dist/wheels/panel-0.14.0-py3-none-any.whl', 'numpy']
  for (const pkg of env_spec) {
    const pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    await self.pyodide.runPythonAsync(`
      import micropip
      await micropip.install('${pkg}');
    `);
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import panel as pn
import base64
import io
import numpy as np
from PIL import Image, ImageFilter
import param
import time

import panel as pn

pn.extension(sizing_mode="stretch_width")

timeout = pn.widgets.IntSlider(name="Timeout", value=1000, start=10, end=1000, step=10)
video_stream = pn.widgets.VideoStream(name='Video Stream', timeout=1000, height=0, width=0, visible=False)
int_slider = pn.widgets.IntSlider(name='Blur Radius', start=0, end=20, value=10, height=100, sizing_mode="stretch_width")
image = pn.pane.JPG(sizing_mode="scale_width", margin=0)
main = pn.Column(
    video_stream, image, int_slider
)
updating = pn.widgets.Checkbox()
last_update = pn.widgets.FloatInput(value=time.time())

def to_pil_img(value):
    encoded_data = value.split(',')[1]
    base64_decoded = base64.b64decode(encoded_data)
    image = Image.open(io.BytesIO(base64_decoded))
    image.draft('RGB',(400,400))
    return image

def transform(pil_img: Image, blur_radius):
    return pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

def from_pil_img(pil_img):
    jpg_image = Image.new("RGB", pil_img.size, (255,255,255))
    jpg_image.paste(pil_img,pil_img)    
    
    buff = io.BytesIO()
    jpg_image.save(buff, format="JPEG", mode="L")
    return buff

@pn.depends(timeout, watch=True)
def set_timeout(value):
    video_stream.timeout = value

@pn.depends(video_stream, watch=True)
def update(value):
    if video_stream.paused:
        return
    video_stream.paused=True
    try:
        start = time.time()
        pil_img = to_pil_img(value)
        now = time.time()
        print("to_pil_img", now-start)
        
        
        start = time.time()
        blurred_image = pil_img
        blurred_image = transform(pil_img, int_slider.value)
        value = from_pil_img(blurred_image)
        now = time.time()
        print("transform", now-start)
        
        start = time.time()
        image.object = value
        now = time.time()
        print("set object", now-start)

        now = time.time()
        print("last_update", now-last_update.value)
        last_update.value=now
    except:
        print("error")
    video_stream.paused=False


settings = pn.Param(video_stream, parameters=["paused", "timeout"])
component=pn.Column(timeout, int_slider, video_stream, image,max_width=600)

pn.template.FastListTemplate(
    site="Awesome Panel",
    title="Video Cam",
    sidebar=[settings],
    main=[component],
).servable()

await write_doc()
  `
  const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
  self.postMessage({
    type: 'render',
    docs_json: docs_json,
    render_items: render_items,
    root_ids: root_ids
  });
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()