import string

import numpy as np
import pandas as pd

from plotnine import (
    aes,
    coord_equal,
    geom_point,
    ggplot,
    guides,
    lims,
    scale_color_identity,
    scale_shape_manual,
)


def test_aesthetics():
    data = pd.DataFrame(
        {
            "a": range(5),
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5,
            "f": 6,
            "g": 7,
            "h": 8,
            "i": 9,
        }
    )

    p = (
        ggplot(data, aes(y="a"))
        + geom_point(aes(x="b"))
        + geom_point(aes(x="c", size="a"))
        + geom_point(aes(x="d", alpha="a"), size=10, show_legend=False)
        + geom_point(aes(x="e", shape="factor(a)"), size=10, show_legend=False)
        + geom_point(aes(x="f", color="factor(a)"), size=10, show_legend=False)
        + geom_point(
            aes(x="g", fill="a"), stroke=0, size=10, show_legend=False
        )
        + geom_point(
            aes(x="h", stroke="a"), fill="white", color="green", size=10
        )
        + geom_point(
            aes(x="i", shape="factor(a)"),
            fill="brown",
            stroke=2,
            size=10,
            show_legend=False,
        )
    )

    assert p == "aesthetics"


def test_no_fill():
    data = pd.DataFrame({"x": range(5), "y": range(5)})

    p = (
        ggplot(data, aes("x", "y"))
        + geom_point(color="red", fill=None, size=5, stroke=1.5)
        + geom_point(
            aes(y="y+1"), color="blue", fill="none", size=5, stroke=1.5
        )
        + geom_point(aes(y="y+2"), color="green", fill="", size=5, stroke=1.5)
        + geom_point(
            aes(y="y+3"), color="yellow", fill="gray", size=5, stroke=1.5
        )
    )

    assert p == "no_fill"


def test_legend_transparency():
    n = 5

    data = pd.DataFrame(
        {
            "x": list(range(n)) * 3,
            "y": [1] * n + [2] * n + [3] * n,
            "color": ["orange"] * n + ["red"] * n + ["#0000FF44"] * n,
        }
    )

    p = (
        ggplot(data, aes("x", "y", color="color"))
        + geom_point(size=25, stroke=3)
        + lims(x=(-2.5, 6.5), y=(-1.5, 5.5))
        + scale_color_identity(guide="legend")
    )
    assert p == "legend_transparency"


class TestColorFillonUnfilledShape:
    data = pd.DataFrame({"x": range(6), "y": range(6), "z": list("aabbcc")})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_point(shape="3", size=10, stroke=3)
        + guides(fill=False)
    )

    # Color  Fill  Result
    # No     No    Black
    # No     Yes   Black
    # Yes    No    Color
    # Yes    Yes   Color

    def test_no_mapping(self):
        assert self.p == "no_mapping"

    def test_fill_only_mapping(self):
        p = self.p + aes(fill="x")
        # Same as above
        assert p == "no_mapping"

    def test_color_only_mapping(self):
        p = self.p + aes(color="z")
        assert p == "color_only_mapping"

    def test_color_fill_mapping(self):
        p = self.p + aes(color="z", fill="x")
        # Same as above
        assert p == "color_only_mapping"


def test_custom_shapes():
    n = 26
    shapes = [rf"$\mathrm{{{x}}}$" for x in string.ascii_uppercase]
    theta = np.linspace(0, 2 * np.pi * (1 - 1 / n), n)

    data = pd.DataFrame(
        {
            "x": np.sin(theta),
            "y": np.cos(theta),
            "theta": theta,
        }
    )

    p = (
        ggplot(data, aes("x", "y", shape="factor(range(n))", color="theta"))
        + geom_point(size=10, show_legend=False)
        + scale_shape_manual(shapes)
        + coord_equal()
    )
    assert p == "custom_shapes"
