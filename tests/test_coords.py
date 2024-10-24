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
    geom_line,
    geom_point,
    ggplot,
    xlim,
)

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
