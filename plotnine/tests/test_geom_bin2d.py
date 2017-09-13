from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_bin2d, theme

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
