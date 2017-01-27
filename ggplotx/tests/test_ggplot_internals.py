from __future__ import absolute_import, division, print_function
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from ggplotx import ggplot, aes, geom_point, geom_histogram, geom_line
from ggplotx import xlab, ylab, labs, ggtitle, xlim, lims, guides
from ggplotx import scale_x_continuous, coord_trans, annotate
from ggplotx import stat_identity, facet_null, theme, theme_gray
from ggplotx.aes import is_calculated_aes, strip_dots
from ggplotx.utils.exceptions import GgplotError

df = pd.DataFrame({'x': np.arange(10),
                   'y': np.arange(10)})


def test_labels():
    """
    Test invalid arguments to chart components
    """
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

    with pytest.raises(GgplotError):
        gg = gg + xlab(None)

    with pytest.raises(GgplotError):
        gg = gg + ylab(None)

    with pytest.raises(GgplotError):
        gg = gg + ggtitle(None)

    with pytest.raises(GgplotError):
        gg = gg + labs('x', 'y')


def test_ggplot_parameters():
    p = ggplot(df, aes('x'))
    assert p.data is df
    assert p.mapping == aes('x')
    assert p.environment.namespace['np'] is np
    assert p.environment.namespace['pd'] is pd

    with pytest.raises(GgplotError):
        ggplot([1, 2, 3], aes('x'))


def test_data_transforms():
    p = ggplot(aes(x='x', y='np.log(y)'), df)
    p = p + geom_point()
    p.draw()

    with pytest.raises(Exception):
        # no numpy available
        p = ggplot(aes(x='depth', y="ap.log(price)"), df)
        p = p + geom_point()
        p.draw()


def test_deepcopy():
    p = ggplot(aes('x'), data=df) + geom_histogram()
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


def test_add_aes():
    df = pd.DataFrame({'var1': [1, 2, 3, 4],
                       'var2': 2})
    p = ggplot(df) + geom_point()
    p += aes('var1', 'var2')

    assert p.mapping == aes('var1', 'var2')
    assert p.labels['x'] == 'var1'
    assert p.labels['y'] == 'var2'


def test_nonzero_indexed_data():
    df = pd.DataFrame({98: {'blip': 0, 'blop': 1},
                       99: {'blip': 1, 'blop': 3}}).T
    p = ggplot(aes(x='blip', y='blop'), data=df) + geom_line()
    p.draw()


def test_inplace_add():
    p = _p = ggplot(df)

    p += aes('x', 'y')
    assert p is _p

    p += geom_point()
    assert p is _p

    p += stat_identity()
    assert p is _p

    p += scale_x_continuous()
    assert p is _p

    p += xlim(0, 10)
    assert p is _p

    p += lims(y=(0, 10))
    assert p is _p

    p += labs(x='x')
    assert p is _p

    p += coord_trans()
    assert p is _p

    p += facet_null()
    assert p is _p

    p += annotate('point', 5, 5, color='red', size=5)
    assert p is _p

    p += guides()
    assert p is _p

    p += theme_gray()
    assert p is _p

    th = _th = theme_gray()
    th += theme(aspect_ratio=1)
    assert th is _th
