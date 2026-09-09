import warnings

import pandas as pd

from plotnine import (
    I,
    aes,
    after_scale,
    geom_bar,
    geom_line,
    geom_point,
    ggplot,
    stage,
)
from plotnine.data import mpg, mtcars


def test_no_after_scale_warning():
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        p.draw_test()  # type: ignore


def test_after_scale_positional_aesthetic_with_legend():
    # A staged positional aesthetic cannot appear in the legend key
    # data, so building the legend must not attempt to evaluate it
    p = ggplot(mpg, aes("drv", "displ", color="drv")) + geom_point(
        aes(x=stage("drv", after_scale="x"))
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]


def test_guide_legend_after_scale():
    def alphen(series, a):
        ha = f"{round(a * 255):#04X}"[2:]
        return [f"{hex_color}{ha}" for hex_color in series]

    data = pd.DataFrame(
        {"var1": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]}
    )
    p = (
        ggplot(
            data,
            aes(
                "var1",
                color="factor(var1)",
                fill=after_scale("alphen(color, .5)"),
            ),
        )
        + geom_bar()
    )

    assert p == "guide_legend_after_scale"


def test_guide_legend_missing_value_for_shapes():
    data = pd.DataFrame({"a": [1, 2, 3], "b": ["a", None, "z"]})
    p = ggplot(data, aes("a", "b")) + geom_point(aes(shape="b"), na_rm=True)
    assert p == "guide_legend_missing_value_for_shapes"


def test_literal_layer_does_not_join_another_layer_guide():
    # A layer with a literal colour has no scale of its own. Its glyph
    # must not join a guide trained from another layer's colour mapping.
    colours = ["red", "green", "blue", "red"]
    data = pd.DataFrame(
        {"x": [1, 2, 3, 4], "y": [1, 4, 9, 16], "c": ["a", "b", "a", "b"]}
    )
    p = (
        ggplot(data, aes("x", "y"))
        + geom_point(aes(colour=I(colours)))
        + geom_line(aes(colour="c"))
    )
    p.draw_test()

    ((_, g),) = p.guides._lookup.values()
    contributing = [
        lp.layer.geom.__class__.__name__ for lp in g._layer_parameters
    ]
    assert contributing == ["geom_line"]
