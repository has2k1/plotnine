from __future__ import absolute_import, division, print_function

import pandas as pd

from plotnine import ggplot, aes, stat_ecdf


df = pd.DataFrame({'x': range(10)})


def test_ecdf():
    p = ggplot(df, aes('x')) + stat_ecdf(size=2)

    assert p == 'ecdf'
