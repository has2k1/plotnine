from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from nose.tools import (assert_true, assert_raises, assert_is,
                        assert_is_not, assert_equal)

import six
import numpy as np
import pandas as pd

from ggplot import *
from . import get_assert_same_ggplot, cleanup, assert_same_elements
assert_same_ggplot = get_assert_same_ggplot(__file__)


def test_chart_components():
    """
    Test invalid arguments to chart components
    """

    df = pd.DataFrame({'x': np.arange(10),
                       'y': np.arange(10)})

    gg = ggplot(df, aes(x='x', y='y'))
    gg = gg + geom_point()
    gg = gg + xlab('xlab')
    gg = gg + ylab('ylab')
    gg = gg + ggtitle('title')

    assert_equal(gg.labels['x'], 'xlab')
    assert_equal(gg.labels['y'], 'ylab')
    assert_equal(gg.labels['title'], 'title')

    gg = gg + labs(x='xlab2', y='ylab2', title='title2')
    assert_equal(gg.labels['x'], 'xlab2')
    assert_equal(gg.labels['y'], 'ylab2')
    assert_equal(gg.labels['title'], 'title2')


@cleanup
def test_data_transforms():
    data = diamonds[:200]
    p = ggplot(aes(x='depth', y='np.log(price)'), data)
    p = p + geom_point()
    p.draw()

    with assert_raises(Exception):
        # no numpy available
        p = ggplot(aes(x='depth', y="ap.log(price)"), data)
        p = p + geom_point()
        p.draw()


def test_deepcopy():
    from copy import deepcopy
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    p2 = deepcopy(p)
    assert_is_not(p, p2)
    # Not sure what we have to do for that...
    assert_is(p.data, p2.data)
    assert_equal(len(p.layers), len(p2.layers))
    assert_is_not(p.layers[0].geom, p2.layers[0].geom)
    assert_equal(len(p.mapping), len(p2.mapping))
    assert_is_not(p.mapping, p2.mapping)
    assert_is(p.mapping.aes_env, p2.mapping.aes_env)
