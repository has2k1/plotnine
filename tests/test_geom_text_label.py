import os

import numpy as np
import pandas as pd
import pytest

from plotnine import (
    aes,
    geom_label,
    geom_point,
    geom_text,
    ggplot,
    scale_size_continuous,
    scale_y_continuous,
)
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineWarning

is_CI = os.environ.get("CI") is not None

n = 5
labels = [
    "ggplot",
    "aesthetics",
    "data",
    "geoms",
    r"$\mathbf{statistics^2}$",
    "scales",
    "coordinates",
]
data = pd.DataFrame(
    {
        "x": [1] * n,
        "y": range(n),
        "label": labels[:n],
        "z": range(n),
        "angle": np.linspace(0, 90, n),
    }
)

adjust_text = {
    "arrowprops": {"color": "red"},
}


def test_text_aesthetics():
    p = (
        ggplot(data, aes(y="y", label="label"))
        + geom_text(aes("x", label="label"), size=15, ha="left")
        + geom_text(
            aes("x+1", angle="angle"), size=15, va="top", show_legend=False
        )
        + geom_text(
            aes("x+2", label="label", alpha="z"), size=15, show_legend=False
        )
        + geom_text(aes("x+3", color="factor(z)"), size=15, show_legend=False)
        + geom_text(aes("x+5", size="z"), ha="right", show_legend=False)
        + scale_size_continuous(range=(12, 30))
        + scale_y_continuous(limits=(-0.5, n - 0.5))
    )

    assert p == "text_aesthetics"


def test_label_aesthetics():
    p = (
        ggplot(data, aes(y="y", label="label"))
        + geom_label(
            aes("x", label="label", fill="z"),
            size=15,
            ha="left",
            show_legend=False,
            boxcolor="red",
        )
        + geom_label(
            aes("x+1", angle="angle"), size=15, va="top", show_legend=False
        )
        + geom_label(
            aes("x+2", label="label", alpha="z"), size=15, show_legend=False
        )
        + geom_label(aes("x+3", color="factor(z)"), size=15, show_legend=False)
        + geom_label(aes("x+5", size="z"), ha="right", show_legend=False)
        + scale_size_continuous(range=(12, 30))
        + scale_y_continuous(limits=(-0.5, n - 0.5))
    )

    assert p == "label_aesthetics"


@pytest.mark.skip("Broken for numpy 2")
def test_adjust_text():
    p = (
        ggplot(mtcars.tail(2), aes("mpg", "disp", label="name"))
        + geom_point(size=5, fill="black")
        + geom_text(adjust_text=adjust_text)
    )
    assert p == "adjust_text"


@pytest.mark.skip("Broken for numpy 2")
def test_adjust_label():
    p = (
        ggplot(mtcars.tail(2), aes("mpg", "disp", label="name"))
        + geom_point(size=5, fill="black")
        + geom_label(adjust_text=adjust_text)
    )
    assert p == "adjust_label"


@pytest.mark.skip("Broken for numpy 2")
def test_adjust_text_default_color():
    adjust_text2 = adjust_text.copy()
    del adjust_text2["arrowprops"]["color"]

    p = (
        ggplot(mtcars.tail(2), aes("mpg", "disp", label="name"))
        + aes(color="factor(cyl)")
        + geom_point(size=5, fill="black")
        + geom_text(adjust_text=adjust_text2)
    )
    assert p == "adjust_text_default_color"


def test_format_missing_values():
    data = pd.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [1, 2, 3, 4],
            "c1": [1.1, 2.2, None, 4],
            "c2": ["1.1", "2.2", None, (4, 0)],
        }
    )
    p = (
        ggplot(data, aes("x", "y"))
        + geom_point()
        + geom_text(
            aes(label="c1"),
            nudge_y=0.03,
            va="bottom",
            color="blue",
            format_string="{}",
        )
        + geom_text(
            aes(label="c2"),
            nudge_y=-0.03,
            va="top",
            color="red",
            format_string="{!r}",
        )
    )
    with pytest.warns(PlotnineWarning):
        assert p == "format_missing_values"
