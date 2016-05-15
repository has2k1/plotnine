from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from .. import ggplot, aes, geom_violin, coord_flip, theme
from .tools import assert_ggplot_equal, cleanup

n = 4
m = 10
df = pd.DataFrame({
    'x': np.repeat([chr(65+i) for i in range(n)], m),
    'y': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10] +
          [-2, 2, 3, 4, 5, 6, 7, 8, 9, 12] +
          [-7, -5, 3, 4, 5, 6, 7, 8, 12, 15] +
          [1, 2, 3, 4, 5, 8, 8, 8, 9, 10]
          )
})


@cleanup
def test_aesthetics():
    p = (ggplot(df, aes('x')) +
         geom_violin(aes(y='y'), size=2) +
         geom_violin(df[:2*m], aes(y='y+25', fill='x'), size=2) +
         geom_violin(df[2*m:], aes(y='y+25', color='x'), size=2) +
         geom_violin(df[2*m:], aes(y='y+50', linetype='x'), size=2))

    assert_ggplot_equal(p, 'aesthetics')
    assert_ggplot_equal(p + coord_flip(), 'aesthetics+coord_flip')


@cleanup
def test_scale():
    p = (ggplot(df, aes('x')) +
         # Red should envelop blue
         geom_violin(aes(y='y'), scale='width',
                     color='red', fill='red', size=2) +
         geom_violin(aes(y='y'), scale='area',
                     color='blue', fill='blue', size=2) +
         geom_violin(df[:36], aes(y='y+25'), scale='count',
                     color='green', size=2) +
         # Yellow should envelop green
         geom_violin(aes(y='y+25'), scale='count',
                     color='yellow', fill='yellow', size=2) +
         geom_violin(df[:36], aes(y='y+25'), scale='count',
                     color='green', fill='green', size=2))
    assert_ggplot_equal(p, 'scale')


@cleanup
def test_quantiles_width_dodge():
    p = (ggplot(df, aes('x')) +
         geom_violin(aes(y='y'),
                     draw_quantiles=[.25, .75], size=2) +
         geom_violin(aes(y='y+25'), color='green',
                     width=0.5, size=2) +
         geom_violin(aes(y='y+50', fill='factor(y%2)'),
                     size=2) +
         theme(facet_spacing={'right': 0.85}))
    assert_ggplot_equal(p, 'quantiles_width_dodge')


@cleanup
def test_no_trim():
    p = (ggplot(df, aes('x')) +
         geom_violin(aes(y='y'), trim=False, size=2))
    assert_ggplot_equal(p, 'no_trim')
