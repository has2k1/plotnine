import pandas as pd
import numpy as np
import pytest

from plotnine import ggplot, aes, geom_raster, theme
from plotnine.exceptions import PlotnineWarning


# To leave enough room for the legend
_theme = theme(subplots_adjust={'right': 0.85})


def _random_grid(n, m=None, seed=123):
    if m is None:
        m = n
    prg = np.random.RandomState(seed)
    g = prg.uniform(size=n*m)
    x, y = np.meshgrid(range(n), range(m))
    df = pd.DataFrame({'x': x.ravel(), 'y': y.ravel(), 'g': g})
    return df


def test_square():
    df = _random_grid(5)
    p = (ggplot(df, aes('x', 'y', fill='g'))
         + geom_raster(interpolation='bilinear')
         )
    p + _theme == 'square'


def test_rectangle():
    df = _random_grid(3, 5)
    p = (ggplot(df, aes('x', 'y', fill='g'))
         + geom_raster(interpolation='bilinear')
         )
    p + _theme == 'rectangle'


def test_gap_no_interpolation():
    df = _random_grid(3, 2)
    df.at[4, 'y'] = 3
    p = (ggplot(df, aes('x', 'y', fill='g'))
         + geom_raster()
         )
    # Warns about uneven vertical intervals
    with pytest.warns(PlotnineWarning):
        p + _theme == 'gap_no_interpolation'


def test_gap_with_interpolation():
    df = _random_grid(3, 2)
    df.at[4, 'y'] = 3
    p = (ggplot(df, aes('x', 'y', fill='g'))
         + geom_raster(interpolation='bilinear')
         )
    # Warns about uneven vertical intervals
    with pytest.warns(PlotnineWarning):
        p + _theme == 'gap_with_interpolation'
