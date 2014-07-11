from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

from ggplot import *

import numpy as np
import pandas as pd


def _build_testing_df():
    rst = np.random.RandomState(42)
    x = np.linspace(0.5, 9.5, num=10)
    y = rst.randn(10)
    ymin = y - rst.uniform(0, 1, size=10)
    ymax = y + rst.uniform(0, 1, size=10)

    df = pd.DataFrame({'x': x, 'y': y, 'ymin': ymin, 'ymax': ymax})
    return df


@cleanup
def test_geom_linerange():
    df = _build_testing_df()
    gg = ggplot(aes(x="x", y="y", ymin="ymin", ymax="ymax"), data=df)
    gg = gg + geom_linerange()
    assert_same_ggplot(gg, "geom_linerange")
