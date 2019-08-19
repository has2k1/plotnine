import warnings

import numpy as np
import pandas as pd

from ..coords import coord_flip
from ..exceptions import PlotnineWarning
from ..utils import log
from .annotate import annotate
from .geom_rug import geom_rug


class _geom_logticks(geom_rug):
    """
    Internal geom implementing drawing of annotation_logticks
    """
    DEFAULT_AES = {}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'sides': 'bl', 'alpha': 1,
                      'color': 'black', 'size': 0.5, 'linetype': 'solid',
                      'lengths': (0.036, 0.0225, 0.012), 'base': 10}
    legend_geom = 'path'

    @staticmethod
    def _check_log_scale(base, sides, panel_params, coord):
        """
        Check the log transforms

        Parameters
        ----------
        base : float or None
            Base of the logarithm in which the ticks will be
            calculated. If ``None``, the base of the log transform
            the scale will be used.
        sides : str (default: bl)
            Sides onto which to draw the marks. Any combination
            chosen from the characters ``btlr``, for *bottom*, *top*,
            *left* or *right* side marks. If ``coord_flip()`` is used,
            these are the sides *after* the flip.
        panel_params : SimpleNamespace
            ``x`` and ``y`` view scale values.
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the geom.

        Returns
        -------
        out : tuple
            The bases (base_x, base_y) to use when generating the ticks.
        """
        def is_log(scale):
            if not hasattr(scale, 'trans'):
                return False
            trans = scale.trans
            return (trans.__class__.__name__.startswith('log') and
                    hasattr(trans, 'base'))

        base_x, base_y = base, base
        x_scale = panel_params.x.scale
        y_scale = panel_params.y.scale
        x_is_log = is_log(x_scale)
        y_is_log = is_log(y_scale)
        if isinstance(coord, coord_flip):
            x_is_log, y_is_log = y_is_log, x_is_log

        if 't' in sides or 'b' in sides:
            if base_x is None:
                if x_is_log:
                    base_x = x_scale.trans.base
                else:  # no log, no defined base. See warning below.
                    base_x = 10

            if not x_is_log:
                warnings.warn(
                    "annotation_logticks for x-axis which does not have "
                    "a log scale. The logticks may not make sense.",
                    PlotnineWarning)
            elif x_is_log and base_x != x_scale.trans.base:
                warnings.warn(
                    "The x-axis is log transformed in base {} ,"
                    "but the annotation_logticks are computed in base {}"
                    "".format(base_x, x_scale.trans.base),
                    PlotnineWarning)

        if 'l' in sides or 'r' in sides:
            if base_y is None:
                if y_is_log:
                    base_y = y_scale.trans.base
                else:  # no log, no defined base. See warning below.
                    base_y = 10

            if not y_is_log:
                warnings.warn(
                    "annotation_logticks for y-axis which does not have "
                    "a log scale. The logticks may not make sense.",
                    PlotnineWarning)
            elif y_is_log and base_y != y_scale.trans.base:
                warnings.warn(
                    "The y-axis is log transformed in base {} ,"
                    "but the annotation_logticks are computed in base {}"
                    "".format(base_y, y_scale.trans.base),
                    PlotnineWarning)
        return base_x, base_y

    @staticmethod
    def _calc_ticks(value_range, base):
        """
        Calculate tick marks within a range

        Parameters
        ----------
        value_range: tuple
            Range for which to calculate ticks.

        Returns
        -------
        out: tuple
            (major, middle, minor) tick locations
        """
        def _minor(x, mid_idx):
            return np.hstack([x[1:mid_idx], x[mid_idx+1:-1]])

        # * Calculate the low and high powers,
        # * Generate for all intervals in along the low-high power range
        #   The intervals are in normal space
        # * Calculate evenly spaced breaks in normal space, then convert
        #   them to log space.
        low = np.floor(value_range[0])
        high = np.ceil(value_range[1])
        arr = base ** np.arange(low, float(high+1))
        n_ticks = base - 1
        breaks = [log(np.linspace(b1, b2, n_ticks+1), base)
                  for (b1, b2) in list(zip(arr, arr[1:]))]

        # Partition the breaks in the 3 groups
        major = np.array([x[0] for x in breaks] + [breaks[-1][-1]])
        if n_ticks % 2:
            mid_idx = n_ticks // 2
            middle = [x[mid_idx] for x in breaks]
            minor = np.hstack([_minor(x, mid_idx) for x in breaks])
        else:
            middle = []
            minor = np.hstack([x[1:-1] for x in breaks])

        return major, middle, minor

    def draw_panel(self, data, panel_params, coord, ax, **params):
        # Any passed data is ignored, the relevant data is created
        sides = params['sides']
        lengths = params['lengths']
        _aesthetics = {
            'size': params['size'],
            'color': params['color'],
            'alpha': params['alpha'],
            'linetype': params['linetype']
        }
        base_x, base_y = self._check_log_scale(
            params['base'], sides, panel_params, coord)

        if 'b' in sides or 't' in sides:
            tick_positions = self._calc_ticks(panel_params.x.range, base_x)
            for (positions, length) in zip(tick_positions, lengths):
                data = pd.DataFrame(dict(x=positions, **_aesthetics))
                super().draw_group(data, panel_params, coord, ax,
                                   length=length, **params)

        if 'l' in sides or 'r' in sides:
            tick_positions = self._calc_ticks(panel_params.y.range, base_y)
            for (positions, length) in zip(tick_positions, lengths):
                data = pd.DataFrame(dict(y=positions, **_aesthetics))
                super().draw_group(data, panel_params, coord, ax,
                                   length=length, **params)


class annotation_logticks(annotate):
    """
    Marginal log ticks.

    If added to a plot that does not have a log10 axis
    on the respective side, a warning will be issued.

    Parameters
    ----------
    sides : str (default: bl)
        Sides onto which to draw the marks. Any combination
        chosen from the characters ``btlr``, for *bottom*, *top*,
        *left* or *right* side marks. If ``coord_flip()`` is used,
        these are the sides *after* the flip.
    alpha : float (default: 1)
        Transparency of the ticks
    color : str | tuple (default: 'black')
        Colour of the ticks
    size : float
        Thickness of the ticks
    linetype : 'solid' | 'dashed' | 'dashdot' | 'dotted' | tuple
        Type of line. Default is *solid*.
    lengths: tuple (default (0.036, 0.0225, 0.012))
        length of the ticks drawn for full / half / tenth
        ticks relative to panel size
    base : float (default: None)
        Base of the logarithm in which the ticks will be
        calculated. If ``None``, the base used to log transform
        the scale will be used.
    """

    def __init__(self, sides='bl', alpha=1, color='black', size=0.5,
                 linetype='solid', lengths=(0.036, 0.0225, 0.012),
                 base=None):
        if len(lengths) != 3:
            raise ValueError(
                "length for annotation_logticks must be a tuple of 3 floats")

        self._annotation_geom = _geom_logticks(sides=sides,
                                               alpha=alpha,
                                               color=color,
                                               size=size,
                                               linetype=linetype,
                                               lengths=lengths,
                                               base=base)
