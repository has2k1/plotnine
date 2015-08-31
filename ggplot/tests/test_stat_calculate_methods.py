from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import warnings
from nose.tools import (assert_equal, assert_is, assert_is_not,
                        assert_raises)

import pandas as pd
from ggplot import *
from ggplot.utils.exceptions import GgplotError

from . import cleanup


@cleanup
def test_stat_bin():
    x = [1, 2, 3]
    y = [1, 2, 3]
    df = pd.DataFrame({'x': x, 'y': y})

    # About the default bins
    gg = ggplot(aes(x='x'), df)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        print(gg + stat_bin())
        res = ['range/30' in str(item.message) for item in w]
        assert any(res)

    # About the ignoring the y aesthetic
    gg = ggplot(aes(x='x', y='y'), df)
    with assert_raises(GgplotError):
        print(gg + stat_bin())
