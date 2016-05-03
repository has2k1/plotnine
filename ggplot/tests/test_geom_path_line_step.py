from __future__ import absolute_import, division, print_function

import pandas as pd

from .. import (ggplot, aes, geom_path, geom_line,
                geom_step, arrow)
from .tools import assert_ggplot_equal, cleanup


# steps with diagonals at the ends
df = pd.DataFrame({
        'x': [1, 2, 3, 3, 4, 4, 5, 5, 6, 7],
        'y': [1, 2, 2, 3, 3, 4, 4, 5, 5, 6],
    })


@cleanup
def test_aesthetics():
    p = (ggplot(df, aes('x', 'y')) +
         geom_path(size=4) +
         geom_path(aes(y='y+2', alpha='x'), size=4,
                   show_legend=False) +
         geom_path(aes(y='y+4'), size=4, linetype='dashed',
                   show_legend=False) +
         geom_path(aes(y='y+6', size='x'), color='red',
                   show_legend=False) +
         geom_path(aes(y='y+8', color='x'), size=4))

    assert_ggplot_equal(p, 'aesthetics')


@cleanup
def test_arrow():
    p = (ggplot(df, aes('x', 'y')) +
         geom_path(size=2, arrow=arrow(ends='both', type='closed')) +
         geom_path(aes(y='y+2'), color='red', size=2,
                   arrow=arrow(angle=60, length=1, ends='first')) +
         geom_path(aes(y='y+4'), color='blue', size=2,
                   arrow=arrow(length=1)))

    assert_ggplot_equal(p, 'arrow')


@cleanup
def test_step():
    p = (ggplot(df, aes('x')) +
         geom_step(aes(y='y'), size=4) +
         geom_step(aes(y='y+2'), color='red',
                   direction='vh', size=4))

    assert_ggplot_equal(p, 'step')


@cleanup
def test_line():
    df2 = df.copy()

    # geom_path plots in given order. geom_line &
    # geom_step sort by x before plotting
    df2['x'] = df['x'].values[::-1]

    p = (ggplot(df2, aes('x')) +
         geom_path(aes(y='y'), size=4) +
         geom_line(aes(y='y+2'), color='blue', size=4) +
         geom_step(aes(y='y+4'), color='red', size=4))

    assert_ggplot_equal(p, 'path_line_step')
