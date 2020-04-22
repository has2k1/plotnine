import numpy as np
import pandas as pd
import pytest

from plotnine import (ggplot, aes, geom_path, geom_line,
                      geom_point, geom_step, arrow, facet_grid)
from plotnine.exceptions import PlotnineWarning


# steps with diagonals at the ends
df = pd.DataFrame({
        'x': [1, 2, 3, 3, 4, 4, 5, 5, 6, 7],
        'y': [1, 2, 2, 3, 3, 4, 4, 5, 5, 6],
    })


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

    assert p == 'aesthetics'


def test_arrow():
    p = (ggplot(df, aes('x', 'y')) +
         geom_path(size=2, arrow=arrow(ends='both', type='closed')) +
         geom_path(aes(y='y+2'), color='red', size=2,
                   arrow=arrow(angle=60, length=0.8, ends='first')) +
         geom_path(aes(y='y+4'), color='blue', size=2,
                   arrow=arrow(length=0.8)))

    assert p == 'arrow'


def test_arrow_facets():
    df = pd.DataFrame({
        'x': [1, 3, 2, 4],
        'y': [10, 9, 10, 9],
        'z': ['a', 'a', 'b', 'b']
    })

    p = (ggplot(df, aes('x', 'y'))
         + geom_path(size=2, arrow=arrow(length=.25))
         + facet_grid('~ z')
         )
    assert p == 'arrow_facets'


def test_step():
    p = (ggplot(df, aes('x')) +
         geom_step(aes(y='y'), size=4) +
         geom_step(aes(y='y+2'), color='red',
                   direction='vh', size=4))

    assert p == 'step'


def test_step_mid():
    df = pd.DataFrame({'x': range(9), 'y': range(9)})
    p = (ggplot(df, aes('x', 'y'))
         + geom_point(size=4)
         + geom_step(direction='mid', size=2)
         )

    assert p == 'step_mid'


def test_line():
    df2 = df.copy()

    # geom_path plots in given order. geom_line &
    # geom_step sort by x before plotting
    df2['x'] = df['x'].values[::-1]

    p = (ggplot(df2, aes('x')) +
         geom_path(aes(y='y'), size=4) +
         geom_line(aes(y='y+2'), color='blue', size=4) +
         geom_step(aes(y='y+4'), color='red', size=4))

    assert p == 'path_line_step'


df_missing = pd.DataFrame({
        'x': [1, 2, 3, 4, 5, 6, 7],
        'y1': [np.nan, 1, 2, 3, 4, np.nan, np.nan],
        'y2': [1, 2, 3, np.nan, np.nan, 6, 7]})


def test_missing_values():
    p = (ggplot(df_missing, aes(x='x'))
         + geom_line(aes(y='y1'), size=2))

    with pytest.warns(PlotnineWarning):
        assert p == 'missing_values'


def test_no_missing_values():
    p = (ggplot(df_missing, aes(x='x'))
         + geom_line(aes(y='y2'), size=2))

    assert p == 'no_missing_values'


def test_groups_less_that_two_points():
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [0, 0, 1, 2, 2],
        'C': [1, 2, 3, 4, 5],
        'D': [1, 2, 3, 4, 5]
    })

    p = (ggplot(df)
         + geom_line(aes(x='A', y='C', group='B', color='D'), size=2)
         )
    p.draw_test()
