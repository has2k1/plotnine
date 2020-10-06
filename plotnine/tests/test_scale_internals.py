from datetime import datetime

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from plotnine import ggplot, aes, geom_point, expand_limits, theme
from plotnine import geom_col, geom_bar, lims, element_text, annotate
from plotnine.scales import scale_color, scale_color_manual
from plotnine.scales import scale_identity
from plotnine.scales import scale_manual
from plotnine.scales import scale_xy
from plotnine.scales.scale_xy import (scale_x_continuous,
                                      scale_y_continuous,
                                      scale_x_discrete,
                                      scale_y_discrete)
from plotnine.scales.scale_alpha import (scale_alpha_discrete,
                                         scale_alpha_continuous)
from plotnine.scales.scale_linetype import (scale_linetype_discrete,
                                            scale_linetype_continuous)
from plotnine.scales.scale_shape import (scale_shape_discrete,
                                         scale_shape_continuous)
from plotnine.scales.scale_size import (scale_size_discrete,
                                        scale_size_continuous,
                                        scale_size_area,
                                        scale_size_radius)
from plotnine.scales.scale_manual import _scale_manual
from plotnine.scales.scales import make_scale
from plotnine.exceptions import PlotnineError, PlotnineWarning

_theme = theme(subplots_adjust={'right': 0.85})


# test palettes
def test_discrete_color_palettes():
    def _assert_all_colors(colors, n, m=0):
        """
        Make sure the first n elements of colors
        are rgb hex strings. And that the last
        m elements are None
        """
        assert(len(colors) == n+m)
        assert(all([c.startswith('#') for c in colors[:n]]))
        if m > 0:
            assert(all([c is None for c in colors[-m:]]))

    sc = scale_color

    s = sc.scale_color_hue()
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = sc.scale_color_grey()
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    # sequential palettes have a maximum of 9 colors
    s = sc.scale_color_brewer(type='seq')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = sc.scale_color_brewer(type='seq')
    colors = s.palette(9)
    _assert_all_colors(colors, 9)

    s = sc.scale_color_brewer(type='seq')
    with pytest.warns(UserWarning):  # upstream warning
        colors = s.palette(15)
    _assert_all_colors(colors, 9, 6)

    # diverging palettes have a maximum of 11 colors
    s = sc.scale_color_brewer(type='div')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = sc.scale_color_brewer(type='div')
    colors = s.palette(11)
    _assert_all_colors(colors, 11)

    s = sc.scale_color_brewer(type='div')
    with pytest.warns(UserWarning):  # upstream warning
        colors = s.palette(21)
    _assert_all_colors(colors, 11, 10)

    # qualitative have varying maximum colors
    s = sc.scale_color_brewer(type='qual')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = sc.scale_color_brewer(type='qual', palette='Accent')
    with pytest.warns(UserWarning):  # upstream warning
        colors = s.palette(12)
    _assert_all_colors(colors, 8, 4)

    s = sc.scale_color_brewer(type='qual', palette='Set3')
    with pytest.warns(UserWarning):  # upstream warning
        colors = s.palette(15)
    _assert_all_colors(colors, 12, 3)


def test_continuous_color_palettes():
    alpha = 0.6
    alphas = [0.1, 0.9, 0.32, 1.0, 0.65]
    colors1 = ['#000000', '#11BB20']
    colors2 = ['#000000', '#003399', '#42BF63', '#191141']
    sc = scale_color

    def _assert(cscale):
        """
        Make color scale palette returns a single color when
        passed a scalar and multiple colors when
        passed a list
        """
        color = cscale.palette(alpha)
        assert(color[0] == '#')

        colors = cscale.palette(alphas)
        assert(all([c[0] == '#' for c in colors]))

    s = sc.scale_color_gradient()
    _assert(s)

    s = sc.scale_color_gradient2()
    _assert(s)

    s = sc.scale_color_gradientn(colors1)
    _assert(s)

    s = sc.scale_color_gradientn(colors2)
    _assert(s)

    s = sc.scale_color_distiller(type='seq')
    _assert(s)

    s = sc.scale_color_distiller(type='div')
    _assert(s)

    with pytest.warns(PlotnineWarning):
        s = sc.scale_color_distiller(type='qual')
    _assert(s)


def test_color_aliases():
    # American and British names should refer to the same scales
    names = ((s, s.replace('color', 'colour'))
             for s in dir(scale_color) if s.startswith('scale_color')
             )

    for a, b in names:
        assert getattr(scale_color, a) is getattr(scale_color, b)


def test_fill_scale_aesthetics():
    for name in scale_color.__dict__:
        if name.startswith('scale_fill'):
            scale = getattr(scale_color, name)
            assert(scale._aesthetics == ['fill'])


def test_linetype_palettes():
    N = 4  # distinct linetypes
    s = scale_linetype_discrete()
    items = s.palette(N)
    assert(len(items) == N)
    assert(all([isinstance(x, str) for x in items]))

    items = s.palette(N+5)
    assert(all([isinstance(x, str) for x in items[:N]]))

    with pytest.raises(PlotnineError):
        s = scale_linetype_continuous()


def test_shape_palettes():
    N = 10  # distinct shapes
    s = scale_shape_discrete()
    items = s.palette(N)
    assert(len(items) == N)
    assert(all([isinstance(x, str) for x in items]))

    items = s.palette(N+5)
    assert(all([isinstance(x, str) for x in items[:N]]))

    with pytest.raises(PlotnineError):
        scale_shape_continuous()


def test_size_palette():
    s = scale_size_discrete()
    items = s.palette(9)
    assert(len(items) == 9)

    s = scale_size_continuous(range=(1, 6))
    frac = 0.5
    value = s.palette(frac**2)
    assert(value == (1+6)*frac)

    # Just test that they work
    s = scale_size_area(range=(1, 6))
    s.palette(frac**2)

    s = scale_size_radius(range=(1, 6))
    s.palette(frac**2)


def test_scale_identity():
    def is_identity_scale(name):
        return (name.startswith('scale_') and
                name.endswith('_identity'))

    for name in scale_identity.__dict__:
        if is_identity_scale(name):
            s = getattr(scale_identity, name)()
            assert s.palette(5) == 5
            assert s.palette([1, 2, 3]) == [1, 2, 3]


def test_scale_manual():
    def is_manual_scale(name):
        return (name.startswith('scale_') and
                name.endswith('_manual'))

    manual_scales = [getattr(scale_manual, name)
                     for name in scale_manual.__dict__
                     if is_manual_scale(name)]

    values = [1, 2, 3, 4, 5]
    for _scale in manual_scales:
        s = _scale(values)
        assert s.palette(2) == values
        assert s.palette(len(values)) == values
        with pytest.warns(PlotnineWarning):
            s.palette(len(values)+1)

    values = {'A': 'red', 'B': 'violet', 'C': 'blue'}
    sc = scale_manual.scale_color_manual(values)
    assert sc.palette(3) == values

    # Breaks are matched with values
    sc1 = scale_manual.scale_color_manual(
        breaks=[True, False],
        values=['blue', 'red']
    )
    sc2 = scale_manual.scale_color_manual(
        breaks=[True, False],
        values=['red', 'blue']
    )
    assert sc1.map([True, False, True, False]) == ['blue', 'red'] * 2
    assert sc2.map([True, False, True, False]) == ['red', 'blue'] * 2


def test_alpha_palette():
    s = scale_alpha_discrete()
    items = s.palette(9)
    assert(len(items) == 9)

    s = scale_alpha_continuous(range=(0.1, 1))
    value = s.palette(0.5)
    assert(value == (0.1+1)/2.0)


def test_xy_palette():
    s = scale_x_discrete()
    value = s.palette(3)
    assert(value == 3)

    s = scale_y_discrete()
    value = s.palette(11.5)
    assert(value == 11.5)

    s = scale_x_continuous()
    value = s.palette(3.63)
    assert(value == 3.63)

    s = scale_y_continuous()
    value = s.palette(11.52)
    assert(value == 11.52)


def test_xy_limits():
    lst = [1, 2, 3]
    arr = np.array(lst)
    series = pd.Series(lst)
    s1 = scale_x_discrete(limits=lst)
    s2 = scale_x_discrete(limits=arr)
    s3 = scale_x_discrete(limits=series)
    assert all(s2.limits == s1.limits)
    assert all(s3.limits == s1.limits)


def test_setting_limits():
    lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    s = scale_x_continuous()
    s.train(lst)
    assert s.limits == (1, 10)

    s = scale_x_continuous(limits=(3, 7))
    s.train(lst)
    assert s.limits == (3, 7)

    s = scale_x_continuous(limits=(3, None))
    s.train(lst)
    assert s.limits == (3, 10)

    s = scale_x_continuous(limits=(None, 7))
    s.train(lst)
    assert s.limits == (1, 7)

    s = scale_color.scale_color_hue(limits=tuple('abcdefg'))
    s.train(['a', 'b', 'a'])
    assert s.limits == tuple('abcdefg')


def test_discrete_xy_scale_limits():
    lst = list('abcd')
    x = pd.Series(pd.Categorical(lst, ordered=True))

    s = scale_x_discrete()
    s.train(x)
    assert s.limits == lst

    s = scale_x_discrete(limits=reversed)
    s.train(x)
    assert s.limits == lst[::-1]


def test_discrete_xy_scale_drop_limits():
    df = pd.DataFrame({
        'x': list('aaaabbbbccccddd'),
        'c': list('112312231233123')
    })

    p = (ggplot(df)
         + geom_bar(aes(x='x', fill='c'))
         + scale_x_discrete(limits=list('abc'))
         )
    assert p == 'discrete_xy_scale_drop_limits'


def test_setting_limits_transformed():
    lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    s = scale_y_continuous(trans='log10')
    s.train(lst)
    assert s.limits == (1, 10)

    s = scale_y_continuous(trans='log10', limits=[2, 7])
    s.train(lst)
    assert s.limits == (np.log10(2), np.log10(7))

    s = scale_y_continuous(trans='log10', limits=[2, None])
    s.train(lst)
    assert s.limits == (np.log10(2), np.log10(10))

    s = scale_y_continuous(trans='log10', limits=[None, 7])
    s.train(lst)
    assert s.limits == (np.log10(1), np.log10(7))


def test_minor_breaks():
    n = 10
    x = np.arange(n)

    # Default
    s = scale_x_continuous()
    s.train(x)
    breaks = s.get_breaks()
    minor_breaks = s.get_minor_breaks(breaks)
    expected_minor_breaks = (breaks[:-1] + breaks[1:])/2
    assert np.allclose(minor_breaks, expected_minor_breaks, rtol=1e-12)

    # List
    expected_minor_breaks = [2, 4, 6, 8]
    s = scale_x_continuous(minor_breaks=expected_minor_breaks)
    s.train(x)
    breaks = s.get_breaks()
    minor_breaks = s.get_minor_breaks(breaks)
    assert np.allclose(minor_breaks, expected_minor_breaks, rtol=1e-12)

    # Callable
    def func(limits):
        return np.linspace(limits[0], limits[1], n)

    s = scale_x_continuous(minor_breaks=func)
    s.train(x)
    breaks = s.get_breaks()
    minor_breaks = s.get_minor_breaks(breaks)
    _breaks = set(breaks)
    expected_minor_breaks = [x for x in np.arange(n) if x not in _breaks]
    assert np.allclose(minor_breaks, expected_minor_breaks, rtol=1e-12)
    assert not (_breaks & set(minor_breaks))

    # Number of minor breaks
    s = scale_x_continuous(limits=[0, 20], minor_breaks=3)
    minor_breaks = s.get_minor_breaks(major=[0, 10, 20])
    expected_minor_breaks = [2.5, 5, 7.5, 12.5, 15, 17.5]
    assert np.allclose(minor_breaks, expected_minor_breaks, rtol=1e-12)


def test_expand_limits():
    df = pd.DataFrame({'x': range(5, 11), 'y': range(5, 11)})
    p = (ggplot(aes('x', 'y'), data=df)
         + geom_point()
         + expand_limits(y=(0, None))
         )
    assert p == 'expand_limits'


def test_bool_mapping():
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [True, False, False]
    })
    p = ggplot(df, aes('x', 'y')) + geom_point()
    assert p == 'bool_mapping'


def test_make_scale_and_datetimes():
    def correct_scale(scale, name):
        return scale.__class__.__name__ == name

    # cpython
    x = pd.Series([datetime(year, 1, 1) for year in [2010, 2026, 2015]])

    assert correct_scale(make_scale('x', x), 'scale_x_datetime')
    assert correct_scale(make_scale('color', x), 'scale_color_datetime')
    assert correct_scale(make_scale('fill', x), 'scale_fill_datetime')
    assert correct_scale(make_scale('size', x), 'scale_size_datetime')
    assert correct_scale(make_scale('alpha', x), 'scale_alpha_datetime')

    # numpy
    x = pd.Series([np.datetime64(i*10, 'D') for i in range(1, 10)])
    assert correct_scale(make_scale('x', x), 'scale_x_datetime')
    assert correct_scale(make_scale('color', x), 'scale_color_datetime')
    assert correct_scale(make_scale('fill', x), 'scale_fill_datetime')
    assert correct_scale(make_scale('size', x), 'scale_size_datetime')
    assert correct_scale(make_scale('alpha', x), 'scale_alpha_datetime')


def test_scale_continous_breaks():
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    breaks = [2, 4, 6, 8, 10]

    # Array breaks should not trip up the conditional checks
    s1 = scale_x_continuous(breaks=breaks, limits=(1, 10))
    s2 = scale_x_continuous(breaks=np.array(breaks), limits=(1, 10))
    s1.train(x)
    s2.train(x)
    assert list(s1.get_breaks()) == list(s2.get_breaks())


def test_scale_without_a_mapping():
    df = pd.DataFrame({
        'x': [1, 2, 3],
    })
    p = (ggplot(df, aes('x', 'x'))
         + geom_point()
         + scale_color.scale_color_continuous())
    with pytest.warns(PlotnineWarning):
        p.draw_test()


def test_scale_discrete_mapping_nulls():
    a = np.array([1, 2, 3], dtype=object)

    sc = _scale_manual([1, 2, 3, 4, 5])
    sc.train(a)
    res = sc.map([1, 2, 3])
    expected = np.array([1, 2, 3])
    npt.assert_array_equal(res, expected)

    sc = _scale_manual([1, None, 3, 4, 5])
    sc.train(a)
    res = sc.map([1, 2, 3])
    expected = np.array([1, np.nan, 3])
    assert res[0] == expected[0]
    assert all(np.isnan([res[1], expected[1]]))
    assert res[2] == expected[2]


def test_scale_continuous_mapping_nulls():
    # Handling of nans
    sc = scale_color.scale_fill_gradient(
        'yellow', 'blue', na_value='green'
    )
    sc.train([1, 10])
    res = sc.map([1, 5, np.nan, 10])
    assert res[2] == 'green'


def test_multiple_aesthetics():

    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [-1, -2, -3]

    })
    p = (ggplot(df, aes('x', 'x', color='factor(x)', fill='factor(y)'))
         + geom_point(size=9, stroke=2)
         + scale_color.scale_color_brewer(
             type='qual', palette=1, aesthetics=['fill', 'color'])
         )
    assert p + _theme == 'multiple_aesthetics'


def test_missing_manual_dict_aesthetic():
    df = pd.DataFrame({
        'x': range(15),
        'y': range(15),
        'c': np.repeat(list('ABC'), 5)
    })

    values = {'A': 'red', 'B': 'violet', 'D': 'blue'}

    p = (ggplot(df, aes('x', 'y', color='c'))
         + geom_point(size=3)
         + scale_manual.scale_color_manual(values)
         )
    assert p + _theme == 'missing_manual_dict_aesthetic'


def test_missing_data_discrete_scale():
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': ['a', 'b', np.nan]
    })

    p = (ggplot(df, aes('a', 'a'))
         + geom_point(aes(fill='b'), stroke=0, size=10)
         )
    assert p + _theme == 'missing_data_discrete_scale'


df = pd.DataFrame({
    'x': range(4),
    'y': range(4),
    'w': list('wxyz'),
    'z': list('abcd')
})

# Order of legend
# The precedence is driven by
# 1. The order in which the scales are added
# 2. Order of aesthetics in the local (geom) aes calls
# 2. Order of aesthetics in the global (ggplot)  aes calls


def test_legend_ordering_global_aethetics_1():
    # 1. color
    # 2. shape
    p = (ggplot(df)
         + aes('x', 'y', color='w', shape='z')
         + geom_point(size=5)
         )

    assert p + _theme == 'legend_ordering_global_aesthetics_1'


def test_legend_ordering_global_aesthetics_2():
    # 1. shape
    # 2. color
    p = (ggplot(df)
         + aes('x', 'y', shape='z', color='w')
         + geom_point(size=5)
         )

    assert p + _theme == 'legend_ordering_global_aesthetics_2'


def test_legend_ordering_local_aethetics_1():
    # 1. color
    # 2. shape
    p = (ggplot(df)
         + aes('x', 'y')
         + geom_point(aes(color='w', shape='z'), size=5)
         )

    assert p + _theme == 'legend_ordering_local_aesthetics_1'


def test_legend_ordering_local_aethetics_2():
    # 1. shape
    # 2. color
    p = (ggplot(df)
         + aes('x', 'y')
         + geom_point(aes(shape='z', color='w'), size=5)
         )

    assert p + _theme == 'legend_ordering_local_aesthetics_2'


def test_legend_ordering_mixed_scope_aesthetics():
    # The local(geom) aesthetics come first.
    # 1. color
    # 2. shape
    p = (ggplot(df)
         + aes('x', 'y', shape='z')
         + geom_point(aes(color='w'), size=5)
         )

    assert p + _theme == 'legend_ordering_mixed_scope_aesthetics'


def test_legend_ordering_added_scales():
    # The first added scale comes first
    # 1. color
    # 2. shape
    p = (ggplot(df)
         + aes('x', 'y')
         + geom_point(aes(shape='z', color='w'), size=5)
         + scale_color.scale_color_discrete()
         )

    assert p + _theme == 'legend_ordering_added_scales'


def test_breaks_and_labels_outside_of_limits():
    df = pd.DataFrame({'x': range(5, 11), 'y': range(5, 11)})
    p = (ggplot(aes('x', 'y'), data=df)
         + geom_point()
         + scale_x_continuous(
             limits=[7, 9.5],
             breaks=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
             labels=['one', 'two', 'three', 'four', 'five', 'six', 'seven',
                     'eight', 'nine', 'ten', 'eleven']
         )
         )
    assert p == 'breaks_and_labels_outside_of_limits'


def test_changing_scale_transform():
    # No warning
    with pytest.warns(None):
        scale_x_continuous(trans='reverse')
        scale_xy.scale_x_reverse(trans='reverse')
        scale_xy.scale_x_log10(trans='log10')

    # Warnings
    with pytest.warns(PlotnineWarning):
        scale_xy.scale_x_reverse(trans='log10')

    with pytest.warns(PlotnineWarning):
        scale_xy.scale_x_datetime(trans='identity')

    s = scale_xy.scale_x_reverse()
    with pytest.warns(PlotnineWarning):
        s.trans = 'log10'


def test_datetime_scale_limits():
    n = 6

    df = pd.DataFrame({
        'x': [datetime(x, 1, 1) for x in range(2000, 2000+n)],
        'y': range(n)
    })

    p = (ggplot(df, aes('x', 'y'))
         + geom_point()
         + lims(x=[datetime(2000, 1, 1), datetime(2007, 1, 1)])
         + theme(axis_text_x=element_text(angle=45))
         )

    assert p == 'datetime_scale_limits'


def test_ordinal_scale():
    df = pd.DataFrame({
        'x': pd.Categorical(list('abcd'), ordered=True),
        'y': [1, 2, 3, 4]
    })

    p = (ggplot(df)
         + aes('x', 'y', color='-y', fill='x')
         + geom_col(size=4)
         + _theme
         )

    assert p + _theme == 'ordinal_scale'


def test_layer_with_only_infs():
    df = pd.DataFrame({'x': ['a', 'b']})
    p = (ggplot(df, aes('x', 'x'))
         + annotate('rect', xmin=-np.inf, xmax=np.inf, ymin=-np.inf,
                    ymax=np.inf, fill='black', alpha=.25)
         + geom_point(color='red', size=3)
         )
    p = p.build_test()
    assert isinstance(p.scales.get_scales('x'), scale_x_discrete)


def test_discrete_scale_exceeding_maximum_number_of_values():
    df = pd.DataFrame({
        # not that it's the second c that triggered a bug in scale_discrete.map
        'x': pd.Categorical(['c', 'a', 'c', 'b', 'c']),
        'y': [0, 1, 2, 2, 3]})
    p = (ggplot(df, aes('x', 'y', color='x', shape='x'))
         + geom_point()
         + scale_color_manual(['red', 'blue'])
         )
    with pytest.warns(PlotnineWarning):
        p.draw()
