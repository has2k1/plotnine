from __future__ import absolute_import, division, print_function

import pandas as pd

from .. import ggplot, aes, geom_abline, geom_point
from .tools import assert_ggplot_equal, cleanup

df = pd.DataFrame({
        'slope': [1, 1],
        'intercept': [1, -1],
        'x': [-1, 1],
        'y': [-1, 1],
        'z': range(2)
    })


@cleanup
def test_aesthetics():
    p = (ggplot(df, aes('x', 'y')) +
         geom_point() +
         geom_abline(
             aes(slope='slope', intercept='intercept'),
             size=2) +
         geom_abline(
             aes(slope='slope', intercept='intercept+.1', alpha='z'),
             size=2) +
         geom_abline(
             aes(slope='slope', intercept='intercept+.2',
                 linetype='factor(z)'),
             size=2) +
         geom_abline(
             aes(slope='slope', intercept='intercept+.3',
                 color='factor(z)'),
             size=2) +
         geom_abline(
             aes(slope='slope', intercept='intercept+.4', size='z')))

    assert_ggplot_equal(p, 'aesthetics')


@cleanup
def test_aes_inheritance():
    # A default line (intercept = 0, slope = 1)
    p = (ggplot(df, aes('x', 'y', color='factor(z)',
                        slope='slope', intercept='intercept')) +
         geom_point(size=10, show_legend=False) +
         geom_abline(size=2))

    assert_ggplot_equal(p, 'aes_inheritance')
