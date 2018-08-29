import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_bin2d, theme, scale_x_log10
from plotnine.tests import layer_data

n = 20  # Make even for best results
reps = np.hstack([np.arange(int(np.ceil(n/2))),
                  np.arange(int(np.ceil(n//2)))[::-1]])
diagonal = np.repeat(np.arange(n), reps)

df = pd.DataFrame({
    'x': np.hstack([diagonal, diagonal]),
    'y': np.hstack([diagonal, diagonal[::-1]])})

_theme = theme(subplots_adjust={'right': 0.85})


def test_drop_true():
    p = ggplot(df, aes('x', 'y')) + geom_bin2d(binwidth=2, drop=True)
    assert p + _theme == 'drop_true'


def test_drop_false():
    p = ggplot(df, aes('x', 'y')) + geom_bin2d(binwidth=2, drop=False)
    assert p + _theme == 'drop_false'


def test_scale_transformed_breaks():
    df = pd.DataFrame({
        'x': [1, 10, 100, 1000],
        'y': range(4)
    })
    p = (ggplot(df, aes('x', 'y'))
         + geom_bin2d(breaks=([5, 50, 500], [0.5, 1.5, 2.5]))
         )
    out1 = layer_data(p)
    out2 = layer_data(p + scale_x_log10())
    np.testing.assert_allclose(out1.xmax, [50, 500])
    np.testing.assert_allclose(out2.xmax, np.log10([50, 500]))
