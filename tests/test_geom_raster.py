import numpy as np
import pandas as pd
import pytest

from plotnine import aes, geom_raster, ggplot
from plotnine.exceptions import PlotnineWarning


def _random_grid(n, m=None, seed=123):
    if m is None:
        m = n
    prg = np.random.RandomState(seed)
    g = prg.uniform(size=n * m)
    x, y = np.meshgrid(range(n), range(m))
    return pd.DataFrame({"x": x.ravel(), "y": y.ravel(), "g": g})


def test_square():
    data = _random_grid(5)
    p = ggplot(data, aes("x", "y", fill="g")) + geom_raster(
        interpolation="bilinear"
    )
    assert p == "square"


def test_rectangle():
    data = _random_grid(3, 5)
    p = ggplot(data, aes("x", "y", fill="g")) + geom_raster(
        interpolation="bilinear"
    )
    assert p == "rectangle"


def test_gap_no_interpolation():
    data = _random_grid(3, 2)
    data.loc[4, "y"] = 3
    p = ggplot(data, aes("x", "y", fill="g")) + geom_raster()
    # Warns about uneven vertical intervals
    with pytest.warns(PlotnineWarning):
        assert p == "gap_no_interpolation"


def test_gap_with_interpolation():
    data = _random_grid(3, 2)
    data.loc[4, "y"] = 3
    p = ggplot(data, aes("x", "y", fill="g")) + geom_raster(
        interpolation="bilinear"
    )
    # Warns about uneven vertical intervals
    with pytest.warns(PlotnineWarning):
        assert p == "gap_with_interpolation"
