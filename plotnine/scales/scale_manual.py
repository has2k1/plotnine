from __future__ import absolute_import, division, print_function

from mizani.palettes import manual_pal

from ..doctools import document
from ..utils import alias
from .scale import scale_discrete


@document
class _scale_manual(scale_discrete):
    """
    Abstract class for manual scales

    Parameters
    ----------
    {superclass_parameters}
    """
    def __init__(self, values, **kwargs):
        self.palette = manual_pal(values)
        scale_discrete.__init__(self, **kwargs)


@document
class scale_color_manual(_scale_manual):
    """
    Custom discrete color scale

    Parameters
    ----------
    values : array_like
        Colors that make up the palette.
    {superclass_parameters}
    """
    aesthetics = ['color']


@document
class scale_fill_manual(_scale_manual):
    """
    Custom discrete fill scale

    Parameters
    ----------
    values : array_like
        Colors that make up the palette.
    {superclass_parameters}
    """
    aesthetics = ['fill']


@document
class scale_shape_manual(_scale_manual):
    """
    Custom discrete shape scale

    Parameters
    ----------
    values : array_like
        Shapes that make up the palette. See
        :mod:`matplotlib.markers.` for list of all possible
        shapes.
    {superclass_parameters}

    See Also
    --------
    :mod:`matplotlib.markers`
    """
    aesthetics = ['shape']


@document
class scale_linetype_manual(_scale_manual):
    """
    Custom discrete linetype scale

    Parameters
    ----------
    values : array_like
        Linetypes that make up the palette.
    {superclass_parameters}

    See Also
    --------
    :mod:`matplotlib.markers`
    """
    aesthetics = ['linetype']


@document
class scale_alpha_manual(_scale_manual):
    """
    Custom discrete alpha scale

    Parameters
    ----------
    values : array_like
        Alpha values (in the [0, 1] range) that make up
        the palette.
    {superclass_parameters}
    """
    aesthetics = ['alpha']


@document
class scale_size_manual(_scale_manual):
    """
    Custom discrete size scale

    Parameters
    ----------
    values : array_like
        Sizes that make up the palette.
    {superclass_parameters}
    """
    aesthetics = ['size']


# American to British spelling
alias('scale_colour_manual', scale_color_manual)
