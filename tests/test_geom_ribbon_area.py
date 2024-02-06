import numpy as np
import pandas as pd

from plotnine import (
    aes,
    after_stat,
    coord_flip,
    facet_wrap,
    geom_area,
    geom_line,
    geom_ribbon,
    ggplot,
    scale_x_continuous,
)

n = 4  # No. of ribbions in a vertical stack
m = 100  # Points
width = 2 * np.pi  # width of each ribbon
x = np.linspace(0, width, m)

data = pd.DataFrame(
    {
        "x": np.tile(x, n),
        "ymin": np.hstack([np.sin(x) + 2 * i for i in range(n)]),
        "ymax": np.hstack([np.sin(x) + 2 * i + 1 for i in range(n)]),
        "z": np.repeat(range(n), m),
    }
)


def test_ribbon_aesthetics():
    p = (
        ggplot(data, aes("x", ymin="ymin", ymax="ymax", group="factor(z)"))
        + geom_ribbon()
        + geom_ribbon(aes("x+width", alpha="z"))
        + geom_ribbon(
            aes("x+2*width", linetype="factor(z)"),
            color="black",
            fill=None,
            size=2,
        )
        + geom_ribbon(aes("x+3*width", color="z"), fill=None, size=2)
        + geom_ribbon(aes("x+4*width", fill="factor(z)"))
        + geom_ribbon(aes("x+5*width", size="z"), color="black", fill=None)
        + scale_x_continuous(
            breaks=[i * 2 * np.pi for i in range(7)],
            labels=["0"] + [rf"${2 * i}\pi$" for i in range(1, 7)],
        )
    )

    assert p == "ribbon_aesthetics"


def test_area_aesthetics():
    p = (
        ggplot(data, aes("x", "ymax+2", group="factor(z)"))
        + geom_area()
        + geom_area(aes("x+width", alpha="z"))
        + geom_area(
            aes("x+2*width", linetype="factor(z)"),
            color="black",
            fill=None,
            size=2,
        )
        + geom_area(aes("x+3*width", color="z"), fill=None, size=2)
        + geom_area(aes("x+4*width", fill="factor(z)"))
        + geom_area(aes("x+5*width", size="z"), color="black", fill=None)
        + scale_x_continuous(
            breaks=[i * 2 * np.pi for i in range(7)],
            labels=["0"] + [rf"${2 * i}\pi$" for i in range(1, 7)],
        )
    )

    assert p == "area_aesthetics"


def test_ribbon_facetting():
    p = (
        ggplot(data, aes("x", ymin="ymin", ymax="ymax", fill="factor(z)"))
        + geom_ribbon()
        + facet_wrap("z")
    )

    assert p == "ribbon_facetting"


def test_ribbon_coord_flip():
    data = pd.DataFrame({"x": [0, 1, 2, 3, 4, 5], "y": [0, 3, 5, 5, 3, 0]})

    p = (
        ggplot(data, aes("x"))
        + geom_ribbon(aes(ymax="y"), ymin=0)
        + coord_flip()
    )

    assert p == "ribbon_coord_flip"


def test_ribbon_where():
    m = 3
    n = 100
    values = np.linspace(0, 2 * m * np.pi, n)
    data = pd.DataFrame({"x": range(n), "sin": np.sin(values)})

    p = (
        ggplot(data, aes("x", "sin"))
        + geom_ribbon(
            aes(ymin=0, ymax="sin", where="sin>0"), fill="blue", alpha=0.2
        )
        + geom_ribbon(
            aes(ymin=0, ymax="sin", where="sin<0"), fill="red", alpha=0.2
        )
        + geom_line()
    )
    assert p == "ribbon_where"


class TestOutlineType:
    x = np.arange(10)
    d = 5
    data = pd.DataFrame(
        {"x": x, "y1": x, "y2": x + 2 * d, "y3": x + 4 * d, "y4": x + 6 * d}
    )

    p = (
        ggplot(data, aes("x", ymax=after_stat("ymin + d")))
        + geom_ribbon(
            aes(ymin="y1"),
            size=1,
            fill="bisque",
            color="orange",
            outline_type="upper",
        )
        + geom_ribbon(
            aes(ymin="y2"),
            size=1,
            fill="khaki",
            color="darkkhaki",
            outline_type="lower",
        )
        + geom_ribbon(
            aes(ymin="y3"),
            size=1,
            fill="plum",
            color="purple",
            outline_type="both",
        )
        + geom_ribbon(
            aes(ymin="y4"),
            size=1,
            fill="lightblue",
            color="cadetblue",
            outline_type="full",
        )
    )

    def test_ribbon_outline_type(self):
        assert self.p == "ribbon_outline_type"

    def test_ribbon_outline_type_coord_flip(self):
        assert self.p + coord_flip() == "ribbon_outline_type_coord_flip"
