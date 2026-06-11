import warnings

import pandas as pd

from plotnine import (
    aes,
    after_scale,
    geom_bar,
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
