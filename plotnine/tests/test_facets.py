from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_point, facet_grid, facet_wrap

n = 10
df = pd.DataFrame({'x': range(n),
                   'y': range(n),
                   'var1': np.repeat(range(n//2), 2),
                   'var2': np.tile(['a', 'b'], n//2)})

g = (ggplot(df, aes('x', 'y')) +
     geom_point(aes(color='factor(var1)'),
                size=5, show_legend=False))


# facet_wrap

def test_facet_wrap_one_var():
    p = g + facet_wrap('~var1')
    assert p == 'facet_wrap_one_var'


def test_facet_wrap_expression():
    p = g + facet_wrap('pd.cut(var1, (0, 2, 4), include_lowest=True)')
    assert p == 'facet_wrap_expression'


def test_facet_wrap_two_vars():
    p = g + facet_wrap('~var1+var2')
    assert p == 'facet_wrap_two_vars'


def test_facet_wrap_label_both():
    p = g + facet_wrap('~var1+var2', labeller='label_both')
    assert p == 'facet_wrap_label_both'


def test_facet_wrap_not_as_table():
    p = g + facet_wrap('~var1', as_table=False)
    assert p == 'facet_wrap_not_as_table'


def test_facet_wrap_direction_v():
    p = g + facet_wrap('~var1', dir='v')
    assert p == 'facet_wrap_direction_v'


def test_facet_wrap_not_as_table_direction_v():
    p = g + facet_wrap('~var1', as_table=False, dir='v')
    assert p == 'facet_wrap_not_as_table_direction_v'


# facet_grid

def test_facet_grid_one_by_one_var():
    p = g + facet_grid('var1~var2')
    assert p == 'facet_grid_one_by_one_var'


def test_facet_grid_expression():
    p = g + facet_grid(
        ['var2', 'pd.cut(var1, (0, 2, 4), include_lowest=True)'])
    assert p == 'facet_grid_expression'


def test_facet_grid_margins():
    p = g + facet_grid('var1~var2', margins=True)
    assert p == 'facet_grid_margins'
