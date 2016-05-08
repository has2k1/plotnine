from __future__ import absolute_import, division, print_function

import pandas as pd
import numpy as np

from .. import ggplot, aes, geom_linerange, geom_pointrange
from .tools import assert_ggplot_equal, cleanup

n = 4
df = pd.DataFrame({
        'x': range(n),
        'y': np.arange(n) + 0.5,
        'ymin': range(n),
        'ymax': range(1, n+1),
        'z': range(n)
    })


@cleanup
def test_linerange_aesthetics():
    p = (ggplot(df, aes('x')) +
         geom_linerange(aes(ymin='ymin', ymax='ymax'), size=2) +
         geom_linerange(aes(ymin='ymin+1', ymax='ymax+1', alpha='z'),
                        size=2) +
         geom_linerange(aes(ymin='ymin+2', ymax='ymax+2',
                            linetype='factor(z)'),
                        size=2) +
         geom_linerange(aes(ymin='ymin+3', ymax='ymax+3', color='z'),
                        size=2) +
         geom_linerange(aes(ymin='ymin+4', ymax='ymax+4', size='z'))
         )
    assert_ggplot_equal(p, 'linerange_aesthetics')


@cleanup
def test_pointrange_aesthetics():
    p = (ggplot(df, aes('x')) +
         geom_pointrange(aes(y='y', ymin='ymin', ymax='ymax'), size=2) +
         geom_pointrange(aes(y='y+1', ymin='ymin+1', ymax='ymax+1',
                             alpha='z'),
                         size=2, show_legend=False) +
         geom_pointrange(aes(y='y+2', ymin='ymin+2', ymax='ymax+2',
                             linetype='factor(z)'),
                         size=2, show_legend=False) +
         geom_pointrange(aes(y='y+3', ymin='ymin+3', ymax='ymax+3',
                             color='z'),
                         size=2, show_legend=False) +
         geom_pointrange(aes(y='y+4', ymin='ymin+4', ymax='ymax+4',
                             size='z'),
                         show_legend=False)
         )
    assert_ggplot_equal(p, 'pointrange_aesthetics')
