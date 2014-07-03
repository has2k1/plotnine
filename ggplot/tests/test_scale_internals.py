from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal, assert_true, assert_raises
import six

from ggplot import *
from . import assert_prints_warning
from ..utils.exceptions import GgplotError


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

    s = scale_color_hue()
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = scale_color_grey()
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    # sequential palettes have a maximum of 9 colors
    s = scale_color_brewer(type='seq')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = scale_color_brewer(type='seq')
    colors = s.palette(9)
    _assert_all_colors(colors, 9)

    s = scale_color_brewer(type='seq')
    with assert_prints_warning():
        colors = s.palette(15)
    _assert_all_colors(colors, 9, 6)

    # diverging palettes have a maximum of 11 colors
    s = scale_color_brewer(type='div')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = scale_color_brewer(type='div')
    colors = s.palette(11)
    _assert_all_colors(colors, 11)

    s = scale_color_brewer(type='div')
    with assert_prints_warning():
        colors = s.palette(21)
    _assert_all_colors(colors, 11, 10)

    # qualitative have varying maximum colors
    s = scale_color_brewer(type='qual')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = scale_color_brewer(type='qual', palette='Accent')
    with assert_prints_warning():
        colors = s.palette(12)
    _assert_all_colors(colors, 8, 4)

    s = scale_color_brewer(type='qual', palette='Set3')
    with assert_prints_warning():
        colors = s.palette(15)
    _assert_all_colors(colors, 12, 3)


def test_continuous_color_palettes():
    alpha = 0.6
    alphas = [0.1, 0.9, 0.32, 1.0, 0.65]
    colors1 = ['#000000', '#11BB20']
    colors2 = ['#000000', '#003399', '#42BF63' , '#191141']

    def _assert(cscale):
        """
        Make color scale palette returns a single color when
        passed a scalar and multiple colors when
        passed a list
        """
        color = cscale.palette(alpha)
        assert(color[0] == '#')

        colors = cscale.palette(alphas)
        assert(all([c[0]=='#' for c in colors]))

    s = scale_color_gradient()
    _assert(s)

    s = scale_color_gradient2()
    _assert(s)

    s = scale_color_gradientn(colors1)
    _assert(s)

    s = scale_color_gradientn(colors2)
    _assert(s)

    s = scale_color_distiller(type='seq')
    _assert(s)

    s = scale_color_distiller(type='div')
    _assert(s)

    with assert_prints_warning():
        s = scale_color_distiller(type='qual')
    _assert(s)


def test_fill_scale_aesthetics():
    lst = [scale_fill_brewer, scale_fill_distiller,
           scale_fill_gradient, scale_fill_gradient2,
           scale_fill_gradientn, scale_fill_grey,
           scale_fill_hue]
    for scale in lst:
        assert(scale.aesthetics == ['fill'])


def test_linetype_palettes():
    N = 4  # distinct linetypes
    s = scale_linetype()
    items = s.palette(N)
    assert(len(items) == N)
    assert(all([isinstance(x, six.string_types) for x in items]))

    items = s.palette(N+5)
    assert(all([isinstance(x, six.string_types) for x in items[:N]]))
    assert(all([x is None for x in items[N:]]))

    with assert_raises(GgplotError):
        s = scale_linetype_continuous()


def test_shape_palettes():
    N = 10  # distinct shapes
    s = scale_shape()
    items = s.palette(N)
    assert(len(items) == N)
    assert(all([isinstance(x, six.string_types) for x in items]))

    items = s.palette(N+5)
    assert(all([isinstance(x, six.string_types) for x in items[:N]]))
    assert(all([x is None for x in items[N:]]))

    with assert_raises(GgplotError):
        s = scale_shape_continuous()


def test_size_palette():
    s = scale_size_discrete()
    items = s.palette(9)
    assert(len(items) == 9)

    s = scale_size_continuous(range=(1, 6))
    value = s.palette(0.5)
    assert(value == (1+6)/2.0)


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
