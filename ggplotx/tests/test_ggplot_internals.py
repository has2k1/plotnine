from __future__ import absolute_import, division, print_function
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from .. import ggplot, aes, geom_point, geom_histogram, geom_line
from .. import xlab, ylab, labs, ggtitle
from ..aes import is_calculated_aes, strip_dots
from ..data import diamonds
from .conftest import cleanup


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

    assert gg.labels['x'] == 'xlab'
    assert gg.labels['y'] == 'ylab'
    assert gg.labels['title'] == 'title'

    gg = gg + labs(x='xlab2', y='ylab2', title='title2')
    assert gg.labels['x'] == 'xlab2'
    assert gg.labels['y'] == 'ylab2'
    assert gg.labels['title'] == 'title2'


@cleanup
def test_data_transforms():
    data = diamonds[:200]
    p = ggplot(aes(x='depth', y='np.log(price)'), data)
    p = p + geom_point()
    p.draw()

    with pytest.raises(Exception):
        # no numpy available
        p = ggplot(aes(x='depth', y="ap.log(price)"), data)
        p = p + geom_point()
        p.draw()


def test_deepcopy():
    p = ggplot(aes(x="price"), data=diamonds) + geom_histogram()
    p2 = deepcopy(p)
    assert p is not p2
    # Not sure what we have to do for that...
    assert p.data is p2.data
    assert len(p.layers) == len(p2.layers)
    assert p.layers[0].geom is not p2.layers[0].geom
    assert len(p.mapping) == len(p2.mapping)
    assert p.mapping is not p2.mapping
    assert p.environment is p2.environment


def test_aes():
    result = aes('weight', 'hp', color='qsec')
    expected = {'x': 'weight', 'y': 'hp', 'color': 'qsec'}
    assert result == expected


def test_calculated_aes():
    mapping1 = aes('x', y='..density..')
    mapping2 = aes('x', y='..density..*2')
    mapping3 = aes('x', y='..density.. + ..count..')
    mapping4 = aes('x', y='func(..density..)')

    assert is_calculated_aes(mapping1) == ['y']
    assert is_calculated_aes(mapping2) == ['y']
    assert is_calculated_aes(mapping3) == ['y']
    assert is_calculated_aes(mapping4) == ['y']

    assert strip_dots(mapping1['y']) == 'density'
    assert strip_dots(mapping2['y']) == 'density*2'
    assert strip_dots(mapping3['y']) == 'density + count'
    assert strip_dots(mapping4['y']) == 'func(density)'


@cleanup
def test_nonzero_indexed_data():
    df = pd.DataFrame({98: {'blip': 0, 'blop': 1},
                       99: {'blip': 1, 'blop': 3}}).T
    p = ggplot(aes(x='blip', y='blop'), data=df) + geom_line()
    p.draw()
