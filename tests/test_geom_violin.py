import numpy as np
import pandas as pd
import pytest

from plotnine import aes, coord_flip, facet_grid, geom_violin, ggplot
from plotnine.data import mtcars

n = 4
m = 10
data = pd.DataFrame(
    {
        "x": np.repeat([chr(65 + i) for i in range(n)], m),
        "y": (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            + [-2, 2, 3, 4, 5, 6, 7, 8, 9, 12]
            + [-7, -5, 3, 4, 5, 6, 7, 8, 12, 15]
            + [1, 2, 3, 4, 5, 8, 8, 8, 9, 10]
        ),
    }
)


class TestAesthetics:
    p = (
        ggplot(data, aes("x"))
        + geom_violin(aes(y="y"), size=2)
        + geom_violin(data[: 2 * m], aes(y="y+25", fill="x"), size=2)
        + geom_violin(data[2 * m :], aes(y="y+25", color="x"), size=2)
        + geom_violin(data[2 * m :], aes(y="y+50", linetype="x"), size=2)
    )

    def test_aesthetics(self):
        assert self.p == "aesthetics"

    def test_aesthetics_coordatalip(self):
        assert self.p + coord_flip() == "aesthetics+coord_flip"


def test_scale():
    p = (
        ggplot(data, aes("x"))
        +
        # Red should envelop blue
        geom_violin(aes(y="y"), scale="width", color="red", fill="red", size=2)
        + geom_violin(
            aes(y="y"), scale="area", color="blue", fill="blue", size=2
        )
        + geom_violin(
            data[:36], aes(y="y+25"), scale="count", color="green", size=2
        )
        +
        # Yellow should envelop green
        geom_violin(
            aes(y="y+25"), scale="count", color="yellow", fill="yellow", size=2
        )
        + geom_violin(
            data[:36],
            aes(y="y+25"),
            scale="count",
            color="green",
            fill="green",
            size=2,
        )
    )
    assert p == "scale"


def test_quantiles_width_dodge():
    p = (
        ggplot(data, aes("x"))
        + geom_violin(aes(y="y"), draw_quantiles=[0.25, 0.75], size=2)
        + geom_violin(aes(y="y+25"), color="green", width=0.5, size=2)
        + geom_violin(aes(y="y+50", fill="factor(y%2)"), size=2)
    )
    assert p == "quantiles_width_dodge"


def test_quantiles_input_checks():
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), draw_quantiles=True)
    with pytest.raises(TypeError):
        geom_violin(aes("x", "y"), draw_quantiles=["A", 0.25])
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), draw_quantiles=[0.25, 1.25])
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), draw_quantiles=[0.0])
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), draw_quantiles=[1.0])
    g = geom_violin(aes("x", "y"), draw_quantiles=np.array([0.25, 0.25]))
    assert isinstance(g.params["draw_quantiles"], np.ndarray)
    g = geom_violin(aes("x", "y"), draw_quantiles=0.5)
    assert isinstance(g.params["draw_quantiles"], np.ndarray)


def test_no_trim():
    p = ggplot(data, aes("x")) + geom_violin(aes(y="y"), trim=False, size=2)
    assert p == "no_trim"


def test_style():
    p = (
        ggplot(data, aes("x"))
        + geom_violin(aes(y="y"), style="right")
        + geom_violin(aes(y="y+25"), style="left")
    )
    assert p == "style"


def test_style_alternating():
    p = (
        ggplot(data, aes("x"))
        + geom_violin(aes(y="y"), style="right-left", fill="green")
        + geom_violin(aes(y="y+25"), style="left-right", fill="yellow")
    )
    assert p == "style_alternating"


def test_style_input_checks():
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), style=True)
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), style=1)
    with pytest.raises(ValueError):
        geom_violin(aes("x", "y"), style="up")


def test_scales_free():
    # GH655
    p = (
        ggplot(mtcars, aes(x="factor(cyl)", y="mpg"))
        + geom_violin()
        + facet_grid("am", "'column'", scales="free")
    )
    assert p == "scales_free"
