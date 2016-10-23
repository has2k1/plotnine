from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from .. import ggplot, aes, geom_bar, geom_col, geom_histogram
from .conftest import cleanup

n = 10  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
df = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                   'z': np.repeat(range(n//2), range(3, n*2, 4))})


@cleanup
def test_bar_count():
    p = (ggplot(df, aes('x')) +
         geom_bar(aes(fill='factor(z)')))

    assert p == 'bar-count'


@cleanup
def test_col():
    # The color indicates reveals the edges and the stacking
    # that is going on.
    p = (ggplot(df) +
         geom_col(aes('x', 'z', fill='factor(z)'), color='black'))

    assert p == 'col'


@cleanup
def test_histogram_count():
    p = (ggplot(df, aes('x')) +
         geom_histogram(aes(fill='factor(z)'), bins=n))

    assert p == 'histogram-count'
