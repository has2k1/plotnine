import pandas as pd

from plotnine import (
    I,
    aes,
    annotate,
    coord_flip,
    geom_label,
    geom_point,
    ggplot,
)
from plotnine.data import mtcars

colours = ["red", "green", "blue", "red"]
data = pd.DataFrame(
    {"x": [1, 2, 3, 4], "y": [1, 4, 9, 16], "c": ["a", "b", "a", "b"]}
)


def test_literal_colours():
    my_colours = pd.cut(
        mtcars["wt"], 3, labels=["red", "blue", "green"]
    ).to_list()
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point(
        aes(colour=I(my_colours)), size=3
    )
    assert p == "literal_colours"


def test_annotate():
    p = (
        ggplot(mtcars, aes("wt", "mpg"))
        + geom_point(colour="grey")
        + annotate(
            "text",
            label="Text in the middle",
            x=I(0.5),
            y=I(0.5),
            size=12,
        )
    )
    assert p == "annotate"


def test_annotate_coord_flip():
    p = (
        ggplot(mtcars, aes("wt", "mpg"))
        + geom_point(colour="grey")
        + annotate("label", label="90/10", x=I(0.9), y=I(0.1), size=12)
        + coord_flip()
    )
    assert p == "annotation_coord_flip"


def test_asis_in_mapping():
    p = (
        ggplot(mtcars)
        + geom_point(aes("wt", "mpg", colour="factor(cyl)"))
        + geom_label(
            aes(x="I(x)", y="I(y)", label="label"),
            pd.DataFrame({"x": [0.5], "y": [0.9], "label": ["a label"]}),
        )
    )
    assert p == "asis_in_mapping"
