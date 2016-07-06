from __future__ import absolute_import, division, print_function

import pandas as pd
import pytest

from .. import ggplot, aes, geom_hline, geom_point
from ..utils.exceptions import GgplotError
from .conftest import cleanup

df = pd.DataFrame({
        'yintercept': [1, 2],
        'x': [-1, 1],
        'y': [0.5, 3],
        'z': range(2)
    })


@cleanup
def test_aesthetics():
    p = (ggplot(df) +
         geom_point(aes('x', 'y')) +
         geom_hline(aes(yintercept='yintercept'), size=2) +
         geom_hline(aes(yintercept='yintercept+.1', alpha='z'),
                    size=2) +
         geom_hline(aes(yintercept='yintercept+.2',
                        linetype='factor(z)'),
                    size=2) +
         geom_hline(aes(yintercept='yintercept+.3',
                        color='factor(z)'),
                    size=2) +
         geom_hline(aes(yintercept='yintercept+.4', size='z')))

    assert p == 'aesthetics'


@cleanup
def test_aes_inheritance():
    with pytest.raises(GgplotError):
        p = (ggplot(df, aes('x', 'y', yintercept='yintercept')) +
             geom_point() +
             geom_hline(size=2))
        print(p)
