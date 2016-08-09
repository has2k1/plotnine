from __future__ import absolute_import, division, print_function

from mizani.palettes import manual_pal

from ..utils import alias
from .scale import scale_discrete


class _scale_manual(scale_discrete):
    """
    Abstract class for manual scales
    """
    def __init__(self, values, **kwargs):
        self.palette = manual_pal(values)
        scale_discrete.__init__(self, **kwargs)


class scale_color_manual(_scale_manual):
    """
    Custom discrete color scale

    Parameters
    ----------
    values : array_like
        Colors that make up the palette
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['color']


class scale_fill_manual(_scale_manual):
    """
    Custom discrete fill scale

    Parameters
    ----------
    values : array_like
        Colors that make up the palette
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['fill']


class scale_shape_manual(_scale_manual):
    """
    Custom discrete shape scale

    Parameters
    ----------
    values : array_like
        Shapes that make up the palette. See
        :mod:`matplotlib.markers.` for list of all possible
        shapes.
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`

    See Also
    --------
    :mod:`matplotlib.markers`
    """
    aesthetics = ['shape']


class scale_linetype_manual(_scale_manual):
    """
    Custom discrete linetype scale

    Parameters
    ----------
    values : array_like
        Linetypes that make up the palette
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`

    See Also
    --------
    :mod:`matplotlib.markers`
    """
    aesthetics = ['linetype']


class scale_alpha_manual(_scale_manual):
    """
    Custom discrete alpha scale

    Parameters
    ----------
    values : array_like
        Alpha values (in the [0, 1] range) that make up
        the palette
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['alpha']


class scale_size_manual(_scale_manual):
    """
    Custom discrete size scale

    Parameters
    ----------
    values : array_like
        Sizes that make up the palette
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['size']


# American to British spelling
alias('scale_colour_manual', scale_color_manual)
