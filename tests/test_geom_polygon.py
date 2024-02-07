import pandas as pd

from plotnine import aes, geom_polygon, ggplot

data = pd.DataFrame(
    {
        "x": ([1, 2, 3, 2] + [5, 6, 7] + [9, 9, 10, 11, 11, 10]),
        "y": ([2, 3, 2, 1] + [1, 3, 1] + [1.5, 2.5, 3, 2.5, 1.5, 1]),
        "z": ([1] * 4 + [2] * 3 + [3] * 6),
    }
)


def test_aesthetics():
    p = (
        ggplot(data, aes("x", group="factor(z)"))
        + geom_polygon(aes(y="y"))
        + geom_polygon(aes(y="y+3", alpha="z"))
        + geom_polygon(
            aes(y="y+6", linetype="factor(z)"),
            color="brown",
            fill=None,
            size=2,
        )
        + geom_polygon(aes(y="y+9", color="z"), fill=None, size=2)
        + geom_polygon(aes(y="y+12", fill="factor(z)"))
        + geom_polygon(
            aes(y="y+15", size="z"), color="yellow", show_legend=False
        )
    )

    assert p == "aesthetics"


def test_no_fill():
    p = (
        ggplot(data, aes("x", group="factor(z)"))
        + geom_polygon(aes(y="y"), fill=None, color="red", size=2)
        + geom_polygon(aes(y="y+2"), fill="none", color="green", size=2)
        + geom_polygon(aes(y="y+4"), fill="none", color="blue", size=2)
    )
    assert p == "no_fill"
