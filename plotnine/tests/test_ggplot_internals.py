from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from plotnine import ggplot, aes, geom_point, geom_histogram
from plotnine import geom_line, geom_bar
from plotnine import xlab, ylab, labs, ggtitle, xlim, lims, guides
from plotnine import scale_x_continuous, coord_trans, annotate
from plotnine import stat_identity, facet_null, theme, theme_gray
from plotnine.aes import get_calculated_aes, strip_calculated_markers
from plotnine.aes import is_valid_aesthetic
from plotnine.exceptions import PlotnineError

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

    with pytest.raises(PlotnineError):
        gg = gg + xlab(None)

    with pytest.raises(PlotnineError):
        gg = gg + ylab(None)

    with pytest.raises(PlotnineError):
        gg = gg + ggtitle(None)

    with pytest.raises(PlotnineError):
        gg = gg + labs('x', 'y')


def test_ggplot_parameters():
    p = ggplot(df, aes('x'))

    assert p.data is df
    assert p.mapping == aes('x')
    assert p.environment.namespace['np'] is np
    assert p.environment.namespace['pd'] is pd

    p = ggplot(data=df, mapping=aes('x'))
    assert p.data is df
    assert p.mapping == aes('x')

    p = ggplot(data=df)
    assert p.data is df
    assert p.mapping == aes()

    p = ggplot(mapping=aes('x'))
    assert p.data is None
    assert p.mapping == aes('x')

    p = ggplot()
    assert p.data is None
    assert p.mapping == aes()

    with pytest.raises(TypeError):
        ggplot([1, 2, 3], aes('x'))


def test_data_transforms():
    p = ggplot(aes(x='x', y='np.log(y)'), df)
    p = p + geom_point()
    p.draw_test()

    with pytest.raises(Exception):
        # no numpy available
        p = ggplot(aes(x='depth', y="ap.log(price)"), df)
        p = p + geom_point()
        p.draw_test()


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


def test_valid_aes_linetypes():
    assert is_valid_aesthetic('solid', 'linetype')
    assert is_valid_aesthetic('--', 'linetype')
    assert not is_valid_aesthetic('tada', 'linetype')
    assert is_valid_aesthetic((0, (3, 2)), 'linetype')
    assert not is_valid_aesthetic((0, (3, 2.0)), 'linetype')
    assert not is_valid_aesthetic((0, (3, 2, 1)), 'linetype')


def test_valid_aes_shapes():
    assert is_valid_aesthetic('o', 'shape')
    assert is_valid_aesthetic((4, 1, 45), 'shape')
    assert not is_valid_aesthetic([4, 1, 45], 'shape')


def test_valid_aes_colors():
    assert is_valid_aesthetic('red', 'color')
    assert is_valid_aesthetic('#FF0000', 'color')
    assert is_valid_aesthetic('#FF000080', 'color')
    assert is_valid_aesthetic((1, 0, 0), 'color')
    assert is_valid_aesthetic((1, 0, 0), 'color')
    assert is_valid_aesthetic((1, 0, 0, 0.5), 'color')


def test_calculated_aes():
    _strip = strip_calculated_markers

    # stat(ae)
    mapping1 = aes('x', y='stat(density)')
    mapping2 = aes('x', y='stat(density*2)')
    mapping3 = aes('x', y='stat(density + count)')
    mapping4 = aes('x', y='func(stat(density))')

    assert get_calculated_aes(mapping1) == ['y']
    assert get_calculated_aes(mapping2) == ['y']
    assert get_calculated_aes(mapping3) == ['y']
    assert get_calculated_aes(mapping4) == ['y']

    assert _strip(mapping1['y']) == 'density'
    assert _strip(mapping2['y']) == 'density*2'
    assert _strip(mapping3['y']) == 'density + count'
    assert _strip(mapping4['y']) == 'func(density)'

    # ..ae..
    mapping1 = aes('x', y='..density..')
    mapping2 = aes('x', y='..density..*2')
    mapping3 = aes('x', y='..density.. + ..count..')
    mapping4 = aes('x', y='func(..density..)')

    assert get_calculated_aes(mapping1) == ['y']
    assert get_calculated_aes(mapping2) == ['y']
    assert get_calculated_aes(mapping3) == ['y']
    assert get_calculated_aes(mapping4) == ['y']

    assert _strip(mapping1['y']) == 'density'
    assert _strip(mapping2['y']) == 'density*2'
    assert _strip(mapping3['y']) == 'density + count'
    assert _strip(mapping4['y']) == 'func(density)'

    df = pd.DataFrame({'x': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})
    p = ggplot(df) + geom_bar(aes(x='x', fill='stat(count + 2)'))
    p.draw_test()

    p = ggplot(df) + geom_bar(aes(x='x', fill='..count.. + 2'))
    p.draw_test()


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
    p.draw_test()


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


def test_rrshift_piping():
    p = df >> ggplot(aes('x', 'y')) + geom_point()
    assert p.data is df

    with pytest.raises(PlotnineError):
        df >> ggplot(df.copy(), aes('x', 'y')) + geom_point()

    with pytest.raises(TypeError):
        'not a dataframe' >> ggplot(aes('x', 'y')) + geom_point()


def test_adding_list_ggplot():
    lst = [
        geom_point(),
        geom_point(aes('x+1', 'y+1')),
        xlab('x-label'),
        coord_trans()
    ]
    g = ggplot() + lst
    assert len(g.layers) == 2
    assert g.labels['x'] == 'x-label'
    assert isinstance(g.coordinates, coord_trans)


def test_string_group():
    p = ggplot(df, aes('x', 'y')) + geom_point(group='pi')
    p.draw_test()
