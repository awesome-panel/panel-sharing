"""We can create a gallery of projects"""
import pytest

from panel_sharing.components.project_gallery import _to_app_title


@pytest.mark.parametrize(
    ["key", "app_name"],
    [
        ("xyz/Cubic Bezier Curve", "Cubic Bezier Curve"),
        ("xyz/cubic bezier curve", "Cubic Bezier Curve"),
        ("xyz/cubic-bezier-curve", "Cubic Bezier Curve"),
        ("xyz/cubic_bezier_curve", "Cubic Bezier Curve"),
        ("cubic_bezier_curve", "Cubic Bezier Curve"),
    ],
)
def test_sort_key(key, app_name):
    """We can sort keys by app name"""
    assert _to_app_title(key) == app_name
