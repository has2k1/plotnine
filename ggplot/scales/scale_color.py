from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.exceptions import gg_warn
from ..utils import palettes
from .utils import rescale_mid
from .utils import hue_pal, brewer_pal, grey_pal, gradient_n_pal
from .scale import scale_discrete, scale_continuous


# Discrete color scales #

# Qualitative colour scale with evenly spaced hues.
# Note: ggplot operates in the hcl space
class scale_color_hue(scale_discrete):
    aesthetics = ['color']

    def __init__(self, h=.01, l=.6, s=.65, color_space='hls', **kwargs):
        kwargs['palette'] = hue_pal(h, l, s, color_space=color_space)
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

    def __init__(self, low='#132B43', high='#56B1F7', **kwargs):
        """
        Create colormap that will be used by the palette
        """
        kwargs['palette'] = gradient_n_pal([low, high],
                                           name='gradient')
        scale_continuous.__init__(self, **kwargs)


class scale_fill_gradient(scale_color_gradient):
    aesthetics = ['fill']


class scale_color_desaturate(scale_color_gradient):
    aesthetics = ['color']
    guide = 'colorbar'

    def __init__(self, color='red', reverse=False, **kwargs):
        color2 = palettes.desaturate(color, 0)
        low, high = color, color2
        if reverse:
            low, high = high, low
        scale_color_gradient.__init__(self, low, high, **kwargs)


class scale_fill_desaturate(scale_color_desaturate):
    aesthetics = ['fill']


# Diverging colour gradient
class scale_color_gradient2(scale_continuous):
    aesthetics = ['color']
    guide = 'colorbar'

    def __init__(self, low='#832424', mid='#FFFFFF',
                 high='#3A3A98', midpoint=0,
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
    guide = 'colorbar'

    def __init__(self, colors, values=None, **kwargs):
        """
        Create colormap that will be used by the palette
        """
        kwargs['palette'] = gradient_n_pal(colors, values, 'gradientn')
        scale_continuous.__init__(self, **kwargs)


class scale_fill_gradientn(scale_color_gradientn):
    aesthetics = ['fill']


class scale_color_distiller(scale_color_gradientn):
    aesthetics = ['color']
    guide = 'colorbar'

    def __init__(self, type='seq', palette=1, values=None, **kwargs):
        """
        Create colormap that will be used by the palette
        """
        if type.lower() in ('qual', 'qualitative'):
            msg = ("Using a discrete colour palette in a continuous scale."
                   "Consider using type = 'seq' or type = 'div' instead")
            gg_warn(msg)

        # Grab 6 colors from brewer and create a gradient palette
        colours = brewer_pal(type, palette)(6)
        scale_color_gradientn.__init__(self, colours, values, **kwargs)


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
scale_colour_desaturate = scale_color_desaturate
scale_colour_gradient = scale_color_gradient
scale_colour_gradient2 = scale_color_gradient2
scale_colour_gradientn = scale_color_gradientn
scale_colour_discrete = scale_color_discrete
scale_colour_continuous = scale_color_continuous
scale_colour_distiller = scale_color_distiller
