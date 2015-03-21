from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
from copy import deepcopy


import numpy as np
from matplotlib.colors import LinearSegmentedColormap, rgb2hex
import brewer2mpl

from ..utils.color import ColorHCL
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


def hue_pal(h=(0 + 15, 360 + 15), c=100, l=65, h_start=0, direction=1):
    """
    Utility for making hue palettes for color schemes.
    """
    c /= 100.
    l /= 100.
    hcl = ColorHCL()

    def func(n):
        y = deepcopy(h)
        if (y[1] - y[0]) % 360 < 1:
            y = (y[0], y[1] - 360. / n)
        hues = []
        for x in np.linspace(y[0], y[1], n):
            hue = ((x + h_start) % 360) * direction
            hues.append(rgb2hex(hcl(hue, c, l)))
        return hues
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
            sys.stderr.write(msg)
            hex_colors = hex_colors + [None] * (n - nmax)
        return hex_colors
    return func


# Discrete color scales #


# Qualitative colour scale with evenly spaced hues.
class scale_color_hue(scale_discrete):
    aesthetics = ['color']

    def __init__(self, h=(0 + 15, 360 + 15), c=100, l=65,
                 h_start=0, direction=1):
        self.palette = hue_pal(h, c, l, h_start, direction)


class scale_fill_hue(scale_color_hue):
    aesthetics = ['fill']


# Sequential, diverging and qualitative colour scales from colorbrewer.org
class scale_color_brewer(scale_discrete):
    aesthetics = ['color']

    def __init__(self, type='seq', palette=1):
        self.palette = brewer_pal(type, palette)


class scale_fill_brewer(scale_color_brewer):
    aesthetics = ['fill']


# Sequential grey colour scale.
class scale_color_grey(scale_discrete):
    aesthetics = ['color']

    def __init__(self, start=0.2, end=0.8):
        self.palette = grey_pal(start, end)


class scale_fill_grey(scale_color_grey):
    aesthetics = ['fill']


# Continuous color scales #


# Smooth gradient between two colours
class scale_color_gradient(scale_continuous):
    aesthetics = ['color']
    guide = 'colorbar'

    def __init__(self, low='#132B43', high='#56B1F7', space='Lab'):
        """
        Create colormap that will be used by the palette
        """
        color_spectrum = [low, high]
        self.colormap = LinearSegmentedColormap.from_list(
            'gradient', color_spectrum)

    def palette(self, values):
        """
        Return colors along a colormap

        Parameters
        ----------
        values : array_like | float
            Numeric(s) in the range (0, 1)
        """
        color_tuples = self.colormap(values)
        try:
            rgb_colors = [rgb2hex(t) for t in color_tuples]
        except IndexError:
            rgb_colors = rgb2hex(color_tuples)
        return rgb_colors


class scale_fill_gradient(scale_color_gradient):
    aesthetics = ['fill']


# Diverging colour gradient
class scale_color_gradient2(scale_color_gradient):
    aesthetics = ['color']

    def __init__(self, low='#832424', mid='#FFFFFF',
                 high='#3A3A98', space='Lab', midpoint=0):
        """
        Create colormap that will be used by the palette
        """
        color_spectrum = [low, mid, high]
        self.colormap = LinearSegmentedColormap.from_list(
            'gradient2', color_spectrum)

        # All rescale functions should have the same signature
        def _rescale_mid(*args, **kwargs):
            return rescale_mid(*args,  mid=midpoint, **kwargs)

        self.rescaler = _rescale_mid


class scale_fill_gradient2(scale_color_gradient2):
    aesthetics = ['fill']


# Smooth colour gradient between n colours
class scale_color_gradientn(scale_color_gradient):
    aesthetics = ['color']

    def __init__(self, colours, values=None, space='Lab'):
        """
        Create colormap that will be used by the palette
        """
        # TODO: Implement values
        color_spectrum = colours
        self.colormap = LinearSegmentedColormap.from_list(
            'gradient2', color_spectrum)


class scale_fill_gradientn(scale_color_gradientn):
    aesthetics = ['fill']


class scale_color_distiller(scale_color_gradientn):
    aesthetics = ['color']

    def __init__(self, type='seq', palette=1, values=None, space='Lab'):
        """
        Create colormap that will be used by the palette
        """
        if type.lower() in ('qual', 'qualitative'):
            sys.stderr.write(_MSG_CONTINUOUS_DISTILLER)
        # Grab 6 colors from brewer and create a gradient palette
        colours = brewer_pal(type, palette)(6)

        # super() does not work well with reloads
        scale_color_gradientn.__init__(self, colours, values, space)


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
