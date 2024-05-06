import warnings

from plotnine import (
    aes,
    geom_point,
    ggplot,
)
from plotnine.data import mtcars


def test_no_after_scale_warning():
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        p.draw_test()  # type: ignore
