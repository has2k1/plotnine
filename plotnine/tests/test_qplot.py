from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd
import pytest
import six

from plotnine import qplot, theme

_theme = theme(subplots_adjust={'right': 0.85})


def test_scalars():
    p = qplot(x=2, y=3)
    assert p == 'scalars'


def test_arrays():
    p = qplot(x=np.arange(5), y=np.arange(5))
    assert p == 'arrays'


def test_string_arrays():
    p = qplot(x='np.arange(5)', y='np.arange(5)')
    assert p == 'string-arrays'


@pytest.mark.skipif(six.PY2, reason="No range")
def test_range():
    p = qplot(x=range(5), y=range(5))

    assert p == 'range'


def test_onlyx():
    p = qplot(x='np.arange(5)')
    assert p == 'onlyx'


def test_onlyy():
    p = qplot(y=np.arange(5))

    # Small displacement in x-label on travis
    assert p == ('range', {'tol': 8})


def test_sample():
    p = qplot(sample='np.arange(5)')
    assert p == 'sample'


def test_multiple_geoms():
    n = 3
    m = 10
    # n stairs of points, each m points high
    df = pd.DataFrame({'x': np.repeat(range(n), m),
                       'y': np.linspace(0, n, n*m)})
    p = qplot('factor(x)', 'y', data=df, geom=("boxplot", "point"))
    assert p == 'multiple_geoms'


def test_series_labelling():
    df = pd.DataFrame({'x_axis_label': [1, 2, 3],
                       'y_axis_label': [1, 2, 3],
                       'color_label': ['a', 'b', 'c']})
    p = qplot(df.x_axis_label, df.y_axis_label, color=df.color_label)
    assert p + _theme == 'series_labelling'
