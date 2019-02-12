import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_bar, geom_col, geom_histogram
from plotnine import theme, scale_x_sqrt, geom_text
from plotnine.tests import layer_data


n = 10  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
df = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                   'z': np.repeat(range(n//2), range(3, n*2, 4))})

_theme = theme(subplots_adjust={'right': 0.85})


def test_bar_count():
    p = ggplot(df, aes('x')) + geom_bar(aes(fill='factor(z)'))

    assert p + _theme == 'bar-count'


def test_col():
    # The color indicates reveals the edges and the stacking
    # that is going on.
    p = (ggplot(df) +
         geom_col(aes('x', 'z', fill='factor(z)'), color='black'))

    assert p + _theme == 'col'


def test_histogram_count():
    p = (ggplot(df, aes('x')) +
         geom_histogram(aes(fill='factor(z)'), bins=n))

    assert p + _theme == 'histogram-count'


def test_scale_transformed_breaks():
    df = pd.DataFrame({'x': np.repeat(range(1, 5), range(1, 5))})
    p = ggplot(df, aes('x')) + geom_histogram(breaks=[1, 2.5, 4])
    out1 = layer_data(p)
    out2 = layer_data(p + scale_x_sqrt())
    np.testing.assert_allclose(out1.xmin, [1, 2.5])
    np.testing.assert_allclose(out2.xmin, np.sqrt([1, 2.5]))


def test_stat_count_int():
    df = pd.DataFrame({'x': ['a', 'b'], 'weight': [1, 2]})

    p = (ggplot(df)
         + aes(x='x', weight='weight', fill='x')
         + geom_bar()
         + geom_text(aes(label='stat(count)'), stat='count')
         )

    assert p + _theme == 'stat-count-int'


def test_stat_count_float():
    df = pd.DataFrame({'x': ['a', 'b'], 'weight': [1.5, 2.5]})

    p = (ggplot(df)
         + aes(x='x', weight='weight', fill='x')
         + geom_bar()
         + geom_text(aes(label='stat(count)'), stat='count')
         )

    assert p + _theme == 'stat-count-float'
