from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd
import six

from plotnine import ggplot, aes, geom_rug, theme

n = 4
seq = np.arange(1, n+1)
df = pd.DataFrame({
        'x': seq,
        'y': seq,
        'z': seq,
    })
_theme = theme(subplots_adjust={'right': 0.85})


def test_aesthetics():
    p = (ggplot(df) +
         geom_rug(aes('x', 'y'), size=2) +
         geom_rug(aes('x+2*n', 'y+2*n', alpha='z'),
                  size=2, sides='tr') +
         geom_rug(aes('x+4*n', 'y+4*n', linetype='factor(z)'),
                  size=2, sides='t') +
         geom_rug(aes('x+6*n', 'y+6*n', color='factor(z)'),
                  size=2, sides='b') +
         geom_rug(aes('x+8*n', 'y+8*n', size='z'),
                  sides='tblr'))

    if six.PY2:
        # Small displacement in y-axis text
        assert p + _theme == ('aesthetics', {'tol': 4})
    else:
        assert p + _theme == 'aesthetics'
