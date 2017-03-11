from __future__ import absolute_import, division, print_function

import pytest
import six

from plotnine.scales import scale_color
from plotnine.scales import scale_identity
from plotnine.scales import scale_manual
from plotnine.scales import scale_xy
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
from plotnine.exceptions import PlotnineError


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
    with pytest.warns(UserWarning):
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
    with pytest.warns(UserWarning):
        colors = s.palette(21)
    _assert_all_colors(colors, 11, 10)

    # qualitative have varying maximum colors
    s = sc.scale_color_brewer(type='qual')
    colors = s.palette(5)
    _assert_all_colors(colors, 5)

    s = sc.scale_color_brewer(type='qual', palette='Accent')
    with pytest.warns(UserWarning):
        colors = s.palette(12)
    _assert_all_colors(colors, 8, 4)

    s = sc.scale_color_brewer(type='qual', palette='Set3')
    with pytest.warns(UserWarning):
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

    with pytest.warns(UserWarning):
        s = sc.scale_color_distiller(type='qual')
    _assert(s)


def test_fill_scale_aesthetics():
    for name in scale_color.__dict__:
        if name.startswith('scale_fill'):
            scale = getattr(scale_color, name)
            assert(scale.aesthetics == ['fill'])


def test_linetype_palettes():
    N = 4  # distinct linetypes
    s = scale_linetype_discrete()
    items = s.palette(N)
    assert(len(items) == N)
    assert(all([isinstance(x, six.string_types) for x in items]))

    items = s.palette(N+5)
    assert(all([isinstance(x, six.string_types) for x in items[:N]]))

    with pytest.raises(PlotnineError):
        s = scale_linetype_continuous()


def test_shape_palettes():
    N = 10  # distinct shapes
    s = scale_shape_discrete()
    items = s.palette(N)
    assert(len(items) == N)
    assert(all([isinstance(x, six.string_types) for x in items]))

    items = s.palette(N+5)
    assert(all([isinstance(x, six.string_types) for x in items[:N]]))

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

    values = [1, 2, 3, 4, 5]
    for name in scale_manual.__dict__:
        if is_manual_scale(name):
            s = getattr(scale_manual, name)(values)
            assert s.palette(2) == values[:2]
            assert s.palette(len(values)) == values
            with pytest.warns(UserWarning):
                s.palette(len(values)+1)


def test_alpha_palette():
    s = scale_alpha_discrete()
    items = s.palette(9)
    assert(len(items) == 9)

    s = scale_alpha_continuous(range=(0.1, 1))
    value = s.palette(0.5)
    assert(value == (0.1+1)/2.0)


def test_xy_palette():
    sc = scale_xy

    s = sc.scale_x_discrete()
    value = s.palette(3)
    assert(value == 3)

    s = sc.scale_y_discrete()
    value = s.palette(11.5)
    assert(value == 11.5)

    s = sc.scale_x_continuous()
    value = s.palette(3.63)
    assert(value == 3.63)

    s = sc.scale_y_continuous()
    value = s.palette(11.52)
    assert(value == 11.52)
