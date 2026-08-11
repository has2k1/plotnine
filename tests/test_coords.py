from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from mizani.transforms import trans

from plotnine import (
    aes,
    coord_cartesian,
    coord_fixed,
    coord_flip,
    coord_trans,
    geom_bar,
    geom_col,
    geom_line,
    geom_point,
    geom_polygon,
    geom_ribbon,
    ggplot,
    xlim,
)
from plotnine.coords.coord import munch_data
from plotnine.data import mtcars

n = 10  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
data = pd.DataFrame(
    {
        "x": np.repeat(range(n + 1), range(n + 1)),
        "z": np.repeat(range(n // 2), range(3, n * 2, 4)),
    }
)

p = ggplot(data, aes("x")) + geom_bar(aes(fill="factor(z)"), show_legend=False)


def test_coord_flip():
    assert p + coord_flip() == "coord_flip"


def test_coord_fixed():
    assert p + coord_fixed(0.5) == "coord_fixed"


def test_coord_trans():
    class double_trans(trans):
        def transform(self, x):
            return np.square(x)

        def inverse(self, x):
            return np.sqrt(x)

    # Warns probably because of a bad value around the left
    # edge of the domain.
    with pytest.warns(RuntimeWarning):
        assert p + coord_trans(y=double_trans()) == "coord_trans"


def test_coord_trans_reverse():
    # coord trans can reverse continuous and discrete data
    p = (
        ggplot(data, aes("factor(x)"))
        + geom_bar(aes(fill="factor(z)"), show_legend=False)
        + coord_trans(x="reverse", y="reverse")
    )
    assert p == "coord_trans_reverse"


def test_coord_trans_backtransforms():
    data = pd.DataFrame({"x": [-np.inf, np.inf], "y": [1, 2]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_line(size=2)
        + xlim(1, 2)
        + coord_trans(x="log10")
    )
    assert p == "coord_trans_backtransform"


def test_coord_trans_munches_polygon_closing_edge():
    # A polygon is a closed ring, but its vertices only trace it open; the
    # edge from the last vertex back to the first must be munched like any
    # other. The triangle's two explicit edges are axis-aligned (straight
    # under log), so only the closing edge curves — if it is left as a
    # straight chord this baseline shows a triangle instead of the arc.
    tri = pd.DataFrame({"x": [1.0, 1.0, 100.0], "y": [100.0, 1.0, 1.0]})
    p = (
        ggplot(tri, aes("x", "y"))
        + geom_polygon(fill="none", color="black", size=1)
        + coord_trans(x="log10", y="log10")
    )
    assert p == "coord_trans_munches_polygon_closing_edge"


def test_munch_interpolates_every_position_aesthetic():
    # Ribbon edges use `ymin` and `ymax` as path coordinates, so both must
    # vary within each munched segment.
    data = pd.DataFrame(
        {
            "x": [0.0, 1.0],
            "y": [3.0, 8.0],
            "ymin": [1.0, 6.0],
            "ymax": [5.0, 10.0],
            "group": [1, 1],
        }
    )

    munched = munch_data(data, np.array([1.0]))

    assert len(munched) > len(data)
    for column in ("x", "y", "ymin", "ymax"):
        values = munched[column].to_numpy()
        assert np.all(np.diff(values) > 0), f"{column} was not interpolated"


def test_coord_trans_ribbon_edges_curve():
    # A smooth transformed ribbon exposes piecewise-constant `ymin` and
    # `ymax` values as stepped edges.
    data = pd.DataFrame({"x": range(6), "y": [3.0, 8, 5, 9, 4, 7]})
    p = (
        ggplot(data, aes("x", ymin="y - 2", ymax="y + 2"))
        + geom_ribbon(alpha=0.5)
        + coord_trans(y="sqrt")
    )
    assert p == "coord_trans_ribbon_edges_curve"


def test_coord_trans_stacked_bars_have_no_spikes():
    # Each stacked segment must be its own polygon. If they merge into one
    # path, the join between consecutive segments becomes a diagonal that
    # munch subdivides into a triangular spike across the bar.
    p = ggplot(mtcars, aes("factor(cyl)", "mpg")) + geom_col() + coord_trans()
    assert p == "coord_trans_stacked_bars_have_no_spikes"


def test_datetime_coord_limits():
    n = 6

    data = pd.DataFrame(
        {
            "x": [datetime(x, 1, 1) for x in range(2000, 2000 + n)],
            "y": range(n),
        }
    )

    p = (
        ggplot(data, aes("x", "y"))
        + geom_point()
        + coord_cartesian(xlim=(datetime(1999, 1, 1), datetime(2006, 1, 1)))
    )

    assert p == "datetime_scale_limits"
