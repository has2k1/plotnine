from __future__ import absolute_import, division, print_function
import string

import numpy as np
import pandas as pd
import pytest

from .. import (ggplot, aes, geom_point, geom_jitter, geom_bar,
                position_jitter, position_jitterdodge,
                position_nudge)
from ..utils.exceptions import GgplotError
from .conftest import cleanup

n = 6
prng = np.random.RandomState(1234567890)
df1 = pd.DataFrame({'x': [1, 2, 1, 2],
                    'y': [1, 1, 2, 2]})
df2 = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                    'z': np.repeat(range(n//2), range(3, n*2, 4))})


@cleanup
def test_jitter():
    df1 = pd.DataFrame({'x': [1, 2, 1, 2],
                       'y': [1, 1, 2, 2]})
    p = (ggplot(df1, aes('x', 'y')) +
         geom_point(size=10) +
         geom_jitter(size=10, color='red', prng=prng) +
         geom_jitter(size=10, color='blue', width=0.1,
                     height=0.1, prng=prng))
    assert p == 'jitter'

    with pytest.raises(GgplotError):
        geom_jitter(position=position_jitter(), width=0.1)


@cleanup
def test_nudge():
    p = (ggplot(df1, aes('x', 'y')) +
         geom_point(size=10) +
         geom_point(size=10, color='red',
                    position=position_nudge(.25, .25)))
    assert p == 'nudge'


@cleanup
def test_stack():
    p = (ggplot(df2, aes('factor(z)')) +
         geom_bar(aes(fill='factor(x)'), position='stack'))
    assert p == 'stack'


@cleanup
def test_fill():
    p = (ggplot(df2, aes('factor(z)')) +
         geom_bar(aes(fill='factor(x)'), position='fill'))
    assert p == 'fill'


@cleanup
def test_dodge():
    p = (ggplot(df2, aes('factor(z)')) +
         geom_bar(aes(fill='factor(x)'), position='dodge'))
    assert p == 'dodge'


@cleanup
def test_jitterdodge():
    df = pd.DataFrame({
        'x': np.ones(n*2),
        'y': np.repeat(np.arange(n), 2),
        'letters': np.repeat(list(string.ascii_lowercase[:n]), 2)})

    p = (ggplot(df, aes('x', 'y', fill='letters')) +
         geom_point(size=10, fill='black') +
         geom_point(size=10, position=position_jitterdodge(prng=prng)))
    assert p == 'jitterdodge'
