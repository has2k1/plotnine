from __future__ import absolute_import, division, print_function
import warnings

import pandas as pd
import pytest

from plotnine import ggplot, aes, stat_bin
from plotnine.exceptions import PlotnineError


def test_stat_bin():
    x = [1, 2, 3]
    y = [1, 2, 3]
    df = pd.DataFrame({'x': x, 'y': y})

    # About the default bins
    gg = ggplot(aes(x='x'), df) + stat_bin()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        gg.draw_test()
        res = ['bins' in str(item.message).lower() for item in w]
        assert any(res)

    # About the ignoring the y aesthetic
    gg = ggplot(aes(x='x', y='y'), df) + stat_bin()
    with pytest.raises(PlotnineError):
        gg.draw_test()
