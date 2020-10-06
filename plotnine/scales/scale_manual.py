from warnings import warn

import numpy as np

from ..doctools import document
from ..exceptions import PlotnineWarning
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
        # Match the values of the scale with the breaks (if given)
        if 'breaks' in kwargs:
            breaks = kwargs['breaks']
            if np.iterable(breaks) and not isinstance(breaks, str):
                if iter(breaks) is breaks:
                    breaks = list(breaks)
                    kwargs['breaks'] = breaks
                values = {b: v for b, v in zip(breaks, values)}

        self._values = values
        scale_discrete.__init__(self, **kwargs)

    def palette(self, n):
        max_n = len(self._values)
        if n > max_n:
            msg = ("Palette can return a maximum of {} values. "
                   "{} were requested from it.")
            warn(msg.format(max_n, n), PlotnineWarning)
        return self._values


@document
class scale_color_manual(_scale_manual):
    """
    Custom discrete color scale

    Parameters
    ----------
    values : array_like
        Colors that make up the palette. The values will be matched with
        the ``limits`` of the scale or the ``breaks`` if provided.
    {superclass_parameters}
    """
    _aesthetics = ['color']


@document
class scale_fill_manual(_scale_manual):
    """
    Custom discrete fill scale

    Parameters
    ----------
    values : array_like
        Colors that make up the palette. The values will be matched with
        the ``limits`` of the scale or the ``breaks`` if provided.
    {superclass_parameters}
    """
    _aesthetics = ['fill']


@document
class scale_shape_manual(_scale_manual):
    """
    Custom discrete shape scale

    Parameters
    ----------
    values : array_like
        Shapes that make up the palette. See
        :mod:`matplotlib.markers.` for list of all possible
        shapes. The values will be matched with the ``limits``
        of the scale or the ``breaks`` if provided.
    {superclass_parameters}

    See Also
    --------
    :mod:`matplotlib.markers`
    """
    _aesthetics = ['shape']


@document
class scale_linetype_manual(_scale_manual):
    """
    Custom discrete linetype scale

    Parameters
    ----------
    values : list-like
        Linetypes that make up the palette.
        Possible values of the list are:

            1. Strings like

            ::

                'solid'                # solid line
                'dashed'               # dashed line
                'dashdot'              # dash-dotted line
                'dotted'               # dotted line
                'None' or ' ' or ''    # draw nothing

            2. Tuples of the form (offset, (on, off, on, off, ....))
               e.g. (0, (1, 1)), (1, (2, 2)), (2, (5, 3, 1, 3))

        The values will be matched with the ``limits`` of the scale
        or the ``breaks`` if provided.
    {superclass_parameters}

    See Also
    --------
    :mod:`matplotlib.markers`
    """
    _aesthetics = ['linetype']

    def map(self, x, limits=None):
        result = super().map(x, limits)
        # Ensure that custom linetypes are tuples, so that they can
        # be properly inserted and extracted from the dataframe
        if len(result) and hasattr(result[0], '__hash__'):
            result = [x if isinstance(x, str) else tuple(x) for x in result]
        return result


@document
class scale_alpha_manual(_scale_manual):
    """
    Custom discrete alpha scale

    Parameters
    ----------
    values : array_like
        Alpha values (in the [0, 1] range) that make up
        the palette. The values will be matched with the
        ``limits`` of the scale or the ``breaks`` if provided.
    {superclass_parameters}
    """
    _aesthetics = ['alpha']


@document
class scale_size_manual(_scale_manual):
    """
    Custom discrete size scale

    Parameters
    ----------
    values : array_like
        Sizes that make up the palette. The values will be matched
        with the ``limits`` of the scale or the ``breaks`` if provided.
    {superclass_parameters}
    """
    _aesthetics = ['size']


# American to British spelling
alias('scale_colour_manual', scale_color_manual)
