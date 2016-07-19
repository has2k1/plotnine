from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from .. import qplot
from .conftest import cleanup


@cleanup
def test_scalars():
    p = qplot(x=2, y=3)
    assert p == 'scalars'


@cleanup
def test_arrays():
    p = qplot(x=np.arange(5), y=np.arange(5))
    assert p == 'arrays'


@cleanup
def test_string_arrays():
    p = qplot(x='np.arange(5)', y='np.arange(5)')
    assert p == 'string-arrays'


@cleanup
def test_range():
    p = qplot(x=range(5), y=range(5))
    assert p == 'range'


@cleanup
def test_onlyx():
    p = qplot(x='np.arange(5)')
    assert p == 'onlyx'


@cleanup
def test_sample():
    p = qplot(sample='np.arange(5)')
    assert p == 'sample'


@cleanup
def test_multiple_geoms():
    n = 3
    m = 10
    # n stairs of points, each m points high
    df = pd.DataFrame({'x': np.repeat(range(n), m),
                       'y': np.linspace(0, n, n*m)})
    p = qplot('factor(x)', 'y', data=df, geom=("boxplot", "point"))
    assert p == 'multiple_geoms'
