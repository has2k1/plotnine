import pandas as pd
import pytest

from plotnine import (
    aes,
    dup_axis,
    geom_point,
    ggplot,
    scale_x_continuous,
    scale_x_datetime,
    sec_axis,
)
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineError

p0 = ggplot(mtcars, aes("wt", "mpg")) + geom_point()


def test_non_monotonic_transform():
    df = pd.DataFrame({"x": [-5.0, 5.0], "y": [0.0, 1.0]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + scale_x_continuous(sec_axis=sec_axis(lambda x: x**2))
    )
    with pytest.raises(PlotnineError, match="monotonic"):
        p.build_test()


def test_labels_copy_requires_breaks_copy():
    with pytest.raises(PlotnineError):
        sec_axis(lambda x: x + 1, labels=None)


def test_datetime_rejects_sec_axis():
    with pytest.raises(PlotnineError):
        scale_x_datetime(sec_axis=dup_axis())


def test_facet_wrap_sec_axis_flags():
    from plotnine import facet_wrap

    # gear: 3 panels in a 2x2 grid -> (1,1), (1,2), (2,1)
    p = (p0 + facet_wrap("gear", nrow=2)).build_test()
    layout = p.layout.layout
    # secondary x on the top edge of each column
    assert list(layout["AXIS_X_SEC"]) == [True, True, False]
    # secondary y on the right edge of each row
    assert list(layout["AXIS_Y_SEC"]) == [False, True, True]
    details = p.layout.get_details()
    assert details[0].axis_x_sec and not details[2].axis_x_sec


def test_facet_grid_sec_axis_flags():
    from plotnine import facet_grid

    # am: 2 rows, gear: 3 cols
    p = (p0 + facet_grid("am", "gear")).build_test()
    layout = p.layout.layout
    is_top = layout["ROW"] == layout["ROW"].min()
    is_right = layout["COL"] == layout["COL"].max()
    assert list(layout["AXIS_X_SEC"]) == is_top.tolist()
    assert list(layout["AXIS_Y_SEC"]) == is_right.tolist()


def test_facet_null_sec_axis_flags():
    p = p0.build_test()
    details = p.layout.get_details()[0]
    assert details.axis_x_sec and details.axis_y_sec
