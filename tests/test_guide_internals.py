import warnings

import pandas as pd

from plotnine import (
    aes,
    after_scale,
    geom_bar,
    geom_point,
    ggplot,
)
from plotnine.data import mtcars


def test_no_after_scale_warning():
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        p.draw_test()  # type: ignore


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
