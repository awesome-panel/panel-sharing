"""Functionality to convert Panel apps to web assembly"""
import sys
from io import StringIO
from logging import Logger
from pathlib import Path

from bokeh.application import application
from panel.io.convert import convert_app

ALERT_STYLE = """
<style>
.alert {
    padding: 0.75rem 1.25rem;
    border: 1px solid transparent;
    border-radius: 0.25rem;
    margin-top: 15px;
    margin-bottom: 15px;
}
.alert a {
    color: rgb(11, 46, 19); /* #002752; */
    font-weight: 700;
    text-decoration: rgb(11, 46, 19);
    text-decoration-color: rgb(11, 46, 19);
    text-decoration-line: none;
    text-decoration-style: solid;
    text-decoration-thickness: auto;
  }
.alert a:hover {
    color: rgb(11, 46, 19);
    font-weight: 700;
    text-decoration: underline;
}
.alert-convert-failed {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
}
.alert-convert-failed hr {
    border-top-color: #f1b0b7;
}
</style>
"""


class MockLogger(Logger):
    """Used to get a handle on error logs from Bokeh

    See https://github.com/holoviz/panel/issues/4089
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.convert_errors = ""

    def error(self, *args, **kwargs):
        self.convert_errors += args[3] + "\n"


class ConversionError(Exception):
    """Raised if the app cannot be converted"""


def _create_error_build(app_html_path: Path, app_js_path: Path, error: str):
    error = error.replace("\n", "<br>")
    app_html_path.parent.mkdir(parents=True, exist_ok=True)
    app_js_path.unlink(missing_ok=True)
    app_html_path.write_text(
        f"""
{ALERT_STYLE}<div class="bk alert alert-convert-failed">{error}</div>
"""
    )


def _get_error_message(app_html_path: Path, app_js_path: Path, out: str, log_out: str) -> str:
    if (
        app_html_path.exists()
        and app_js_path.exists()
        and out.startswith("Successfully converted")
        and not log_out
    ):
        return ""

    if "ModuleNotFoundError" in log_out:
        out = """Failed to convert. Make sure you only import packages already installed on the
server.\n"""

    if out.startswith("Failed to convert"):
        error = out + "\n" + log_out
    else:
        error = f"""
    Failed to convert:

    {log_out}
    """
    return error


def _convert_project(app: str = "source/app.py", dest_path: str = "build", requirements="auto"):
    """Helper function"""
    build_dir = Path(dest_path)
    build_dir.mkdir(parents=True, exist_ok=True)

    temp_out = StringIO()
    sys.stdout = temp_out

    original_log = application.log
    application.log = MockLogger("bokeh.application.application")

    convert_app(
        app=Path(app),  # type: ignore
        dest_path=Path(dest_path),  # type: ignore
        requirements=requirements,
        prerender=True,
    )

    out = temp_out.getvalue()
    log_out = application.log.convert_errors
    sys.stdout = sys.__stdout__
    application.log = original_log

    app_html_path = build_dir / "app.html"
    app_js_path = build_dir / "app.js"

    error = _get_error_message(
        app_html_path=app_html_path,
        app_js_path=app_js_path,
        out=out,
        log_out=log_out,
    )

    if error:
        _create_error_build(app_html_path=app_html_path, app_js_path=app_js_path, error=error)
        raise ConversionError(error)
