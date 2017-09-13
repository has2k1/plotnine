from __future__ import absolute_import, division, print_function
import string

import numpy as np
import pandas as pd
import pytest

from plotnine import (ggplot, aes, geom_point, geom_jitter, geom_bar,
                      geom_col, geom_text, position_dodge,
                      position_jitter, position_jitterdodge,
                      position_nudge, position_stack, theme)
from plotnine.positions.position import position
from plotnine.exceptions import PlotnineError

n = 6
random_state = np.random.RandomState(1234567890)
df1 = pd.DataFrame({'x': [1, 2, 1, 2],
                    'y': [1, 1, 2, 2]})
df2 = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                    'z': np.repeat(range(n//2), range(3, n*2, 4))})
_theme = theme(subplots_adjust={'right': 0.85})


def test_jitter():
    df1 = pd.DataFrame({'x': [1, 2, 1, 2],
                        'y': [1, 1, 2, 2]})
    p = (ggplot(df1, aes('x', 'y')) +
         geom_point(size=10) +
         geom_jitter(size=10, color='red', random_state=random_state) +
         geom_jitter(size=10, color='blue', width=0.1,
                     height=0.1, random_state=random_state))
    assert p + _theme == 'jitter'

    with pytest.raises(PlotnineError):
        geom_jitter(position=position_jitter(), width=0.1)


def test_nudge():
    p = (ggplot(df1, aes('x', 'y')) +
         geom_point(size=10) +
         geom_point(size=10, color='red',
                    position=position_nudge(.25, .25)))
    assert p + _theme == 'nudge'


def test_stack():
    p = (ggplot(df2, aes('factor(z)')) +
         geom_bar(aes(fill='factor(x)'), position='stack'))
    assert p + _theme == 'stack'


def test_stack_negative():
    df = df1.copy()
    _loc = df.columns.get_loc
    df.iloc[0, _loc('y')] *= -1
    df.iloc[len(df)-1, _loc('y')] *= -1
    p = (ggplot(df)
         + geom_col(aes('factor(x)', 'y', fill='factor(y)'),
                    position='stack')
         + geom_text(aes('factor(x)', 'y', label='y'),
                     position=position_stack(vjust=0.5))
         )

    assert p + _theme == 'stack-negative'


def test_fill():
    p = (ggplot(df2, aes('factor(z)')) +
         geom_bar(aes(fill='factor(x)'), position='fill'))
    assert p + _theme == 'fill'


def test_dodge():
    p = (ggplot(df2, aes('factor(z)')) +
         geom_bar(aes(fill='factor(x)'), position='dodge'))
    assert p + _theme == 'dodge'


def test_dodge_preserve_single():
    df1 = pd.DataFrame({'x': ['a', 'b', 'b'],
                        'y': ['a', 'a', 'b']})
    p = (ggplot(df1, aes('x', fill='y')) +
         geom_bar(position=position_dodge(preserve='single')))
    assert p + _theme == 'dodge_preserve_single'


def test_jitterdodge():
    df = pd.DataFrame({
        'x': np.ones(n*2),
        'y': np.repeat(np.arange(n), 2),
        'letters': np.repeat(list(string.ascii_lowercase[:n]), 2)})
    position = position_jitterdodge(random_state=random_state)

    p = (ggplot(df, aes('x', 'y', fill='letters')) +
         geom_point(size=10, fill='black') +
         geom_point(size=10, position=position))
    assert p + _theme == 'jitterdodge'


def test_position_from_geom():
    geom = geom_point(position='jitter')
    assert isinstance(position.from_geom(geom), position_jitter)

    geom = geom_point(position='position_jitter')
    assert isinstance(position.from_geom(geom), position_jitter)

    geom = geom_point(position=position_jitter())
    assert isinstance(position.from_geom(geom), position_jitter)

    geom = geom_point(position=position_jitter)
    assert isinstance(position.from_geom(geom), position_jitter)
