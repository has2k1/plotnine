from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, rgb2hex
import brewer2mpl

from ..utils.exceptions import gg_warning, GgplotError
from ..utils import palettes
from .utils import rescale_mid
from .scale import scale_discrete, scale_continuous

_TPL_MAX_PALETTE_COLORS = """Warning message:
Brewer palette {} has a maximum of {} colors
Returning the palette you asked for with that many colors
"""

_MSG_CONTINUOUS_DISTILLER = """\
Using a discrete colour palette in a continuous scale.
Consider using type = "seq" or type = "div" instead"
"""
# Palette making utilities #


def hue_pal(h=.01, l=.6, s=.65):
    """
    Utility for making hue palettes for color schemes.
    """
    if not all([0<=val<=1 for val in (h, l, s)]):
        msg = ("hue_pal expects values to be between 0 and 1.",
               " I got h={}, l={}, s={}".format(h, l, s))
        raise GgplotError(*msg)

    def func(n):
        colors = palettes.hls_palette(n, h, l, s)
        return [rgb2hex(c) for c in colors]
    return func


def grey_pal(start=0.2, end=0.8):
    """
    Utility for creating discrete grey scale palette
    """
    gamma = 2.2
    ends = ((0.0, start, start), (1.0, end, end))
    cdict = {'red': ends, 'green': ends, 'blue': ends}
    grey_cmap = LinearSegmentedColormap('grey', cdict)

    def func(n):
        colors = []
        # The grey scale points are linearly separated in
        # gamma encoded space
        for x in np.linspace(start**gamma, end**gamma, n):
            # Map points onto the [0, 1] palette domain
            x = (x ** (1./gamma) - start) / (end - start)
            colors.append(rgb2hex(grey_cmap(x)))
        return colors
    return func


def brewer_pal(type='seq', palette=1):
    """
    Utility for making a brewer palette
    """
    def _handle_shorthand(text):
        abbrevs = {
            "seq": "Sequential",
            "qual": "Qualitative",
            "div": "Diverging"
        }
        text = abbrevs.get(text, text)
        return text.title()

    def _number_to_palette(ctype, n):
        n -= 1
        palettes = sorted(brewer2mpl.COLOR_MAPS[ctype].keys())
        if n < len(palettes):
            return palettes[n]

    def _max_palette_colors(type, palette_name):
        """
        Return the number of colors in the brewer palette
        """
        if type == 'Sequential':
            return 9
        elif type == 'Diverging':
            return 11
        else:
            # Qualitative palettes have different limits
            qlimit = {"Accent": 8, "Dark": 8, "Paired": 12,
                      "Pastel1": 9, "Pastel2": 8, "Set1": 9,
                      "Set2": 8, "Set3": 12}
            return qlimit[palette_name]

    type = _handle_shorthand(type)
    if isinstance(palette, int):
        palette_name = _number_to_palette(type, palette)
    else:
        palette_name = palette
    nmax = _max_palette_colors(type, palette_name)

    def func(n):
        # Only draw the maximum allowable colors from the palette
        # and fill any remaining spots with None
        _n = n if n <= nmax else nmax
        bmap = brewer2mpl.get_map(palette_name, type, _n)
        hex_colors = bmap.hex_colors
        if n > nmax:
            msg = _TPL_MAX_PALETTE_COLORS.format(palette_name, nmax)
            gg_warning(msg)
            hex_colors = hex_colors + [None] * (n - nmax)
        return hex_colors
    return func


def gradient_n_pal(colors, values=None, name='gradientn'):
    if values is None:
        colormap = LinearSegmentedColormap.from_list(
            name, colors)
    else:
        colormap = LinearSegmentedColormap.from_list(
            name, list(zip(values, colors)))

    def func(vals):

        """
        Return colors along a colormap

        Parameters
        ----------
        values : array_like | float
            Numeric(s) in the range (0, 1)
        """
        color_tuples = colormap(vals)
        try:
            rgb_colors = [rgb2hex(t) for t in color_tuples]
        except IndexError:
            rgb_colors = rgb2hex(color_tuples)
        return rgb_colors
    return func

# Discrete color scales #


# Qualitative colour scale with evenly spaced hues.
# Note: ggplot operates in the hcl space
class scale_color_hue(scale_discrete):
    aesthetics = ['color']

    def __init__(self, h=.01, l=.6, s=.65, **kwargs):
        kwargs['palette'] = hue_pal(h, l, s)
        scale_discrete.__init__(self, **kwargs)


class scale_fill_hue(scale_color_hue):
    aesthetics = ['fill']


# Sequential, diverging and qualitative colour scales from colorbrewer.org
class scale_color_brewer(scale_discrete):
    aesthetics = ['color']

    def __init__(self, type='seq', palette=1, **kwargs):
        kwargs['palette'] = brewer_pal(type, palette)
        scale_discrete.__init__(self, **kwargs)


class scale_fill_brewer(scale_color_brewer):
    aesthetics = ['fill']


# Sequential grey colour scale.
class scale_color_grey(scale_discrete):
    aesthetics = ['color']

    def __init__(self, start=0.2, end=0.8, **kwargs):
        kwargs['palette'] = grey_pal(start, end)
        scale_discrete.__init__(self, **kwargs)


class scale_fill_grey(scale_color_grey):
    aesthetics = ['fill']


# Continuous color scales #


# Smooth gradient between two colours
class scale_color_gradient(scale_continuous):
    aesthetics = ['color']
    guide = 'colorbar'

    def __init__(self, low='#132B43', high='#56B1F7', space='Lab', **kwargs):
        """
        Create colormap that will be used by the palette
        """
        kwargs['palette'] = gradient_n_pal([low, high],
                                           name='gradient')
        scale_continuous.__init__(self, **kwargs)


class scale_fill_gradient(scale_color_gradient):
    aesthetics = ['fill']


# Diverging colour gradient
class scale_color_gradient2(scale_continuous):
    aesthetics = ['color']

    def __init__(self, low='#832424', mid='#FFFFFF',
                 high='#3A3A98', space='Lab', midpoint=0,
                 **kwargs):
        """
        Create colormap that will be used by the palette
        """
        # All rescale functions should have the same signature
        def _rescale_mid(*args, **kwargs):
            return rescale_mid(*args,  mid=midpoint, **kwargs)

        kwargs['rescaler'] = _rescale_mid
        kwargs['palette'] = gradient_n_pal([low, mid, high],
                                           name='gradient2')
        scale_continuous.__init__(self, **kwargs)


class scale_fill_gradient2(scale_color_gradient2):
    aesthetics = ['fill']


# Smooth colour gradient between n colours
class scale_color_gradientn(scale_continuous):
    aesthetics = ['color']

    def __init__(self, colors, values=None, space='Lab', **kwargs):
        """
        Create colormap that will be used by the palette
        """
        kwargs['palette'] = gradient_n_pal(colors, values, 'gradientn')
        scale_continuous.__init__(self, **kwargs)


class scale_fill_gradientn(scale_color_gradientn):
    aesthetics = ['fill']


class scale_color_distiller(scale_color_gradientn):
    aesthetics = ['color']

    def __init__(self, type='seq', palette=1, values=None,
                 space='Lab', **kwargs):
        """
        Create colormap that will be used by the palette
        """
        if type.lower() in ('qual', 'qualitative'):
            gg_warning(_MSG_CONTINUOUS_DISTILLER)

        # Grab 6 colors from brewer and create a gradient palette
        colours = brewer_pal(type, palette)(6)
        scale_color_gradientn.__init__(self, colours, values,
                                       space, **kwargs)


class scale_fill_distiller(scale_color_distiller):
    aesthetics = ['fill']


# Default scales
scale_color_discrete = scale_color_hue
scale_color_continuous = scale_color_gradient
scale_fill_discrete = scale_fill_hue
scale_fill_continuous = scale_fill_gradient

# American to British spelling
scale_colour_hue = scale_color_hue
scale_colour_grey = scale_color_grey
scale_colour_brewer = scale_color_brewer
scale_colour_gradient = scale_color_gradient
scale_colour_gradient2 = scale_color_gradient2
scale_colour_gradientn = scale_color_gradientn
scale_colour_discrete = scale_color_discrete
scale_colour_continuous = scale_color_continuous
scale_colour_distiller = scale_color_distiller
