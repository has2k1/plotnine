import warnings

import numpy as np
import pandas as pd
import mizani.transforms

from ..coords import coord_flip
from ..exceptions import PlotnineWarning
from .annotate import annotate
from .geom_rug import geom_rug


class _geom_logticks(geom_rug):
    """internal geom implementing drawing of annotation_logticks"""

    DEFAULT_AES = {}
    DEFAULT_PARAMS = {
        'stat': 'identity',
        'position': 'identity',
        'na_rm': False,
        'sides': 'bl',
        'alpha': 1,
        'color': 'black',
        'size': 0.5,
        'linetype': 'solid',
        'lengths': (0.036, 0.0225, 0.012),
    }
    legend_geom = 'path'

    @staticmethod
    def _check_log_scale(sides, x_is_log_10, y_is_log_10, is_coord_flip):
        if is_coord_flip:
            x_is_log_10, y_is_log_10 = y_is_log_10, x_is_log_10
        result = []
        if (not x_is_log_10 and ('t' in sides or 'b' in sides)):
            warnings.warn("annotation_logticks for x-axis,"
                          " but x-axis is not log10 - nonsensical marks show.",
                          PlotnineWarning)
        if (not y_is_log_10 and ('l' in sides or 'r' in sides)):
            warnings.warn("annotation_logticks for y-axis,"
                          " but y-axis is not log10 - nonsensical marks show.",
                          PlotnineWarning)
        return result

    @classmethod
    def draw_panel(cls, data, panel_params, coord, ax, **params):
        cls._check_log_scale(
            params["sides"],
            isinstance(panel_params["scales"].x.trans,
                       mizani.transforms.log10_trans),
            isinstance(panel_params["scales"].y.trans,
                       mizani.transforms.log10_trans),
            isinstance(coord, coord_flip),
        )
        if 'l' in params['sides'] or 'r' in params['sides']:
            cls.draw_group('y', panel_params['y_range'],
                           panel_params, coord, ax, params)
        if 'b' in params['sides'] or 't' in params['sides']:
            cls.draw_group('x', panel_params['x_range'],
                           panel_params, coord, ax, params)

    @classmethod
    def draw_group(cls, axis, range, panel_params, coord, ax,
                   params):
        positions = cls._calc_ticks(range)
        lengths = params.get('lengths', cls.DEFAULT_PARAMS['lengths'])
        if 'lengths' in params:
            del params['lengths']

        for (positions, length) in zip(positions, lengths):
            data = pd.DataFrame({
                axis: positions,
                'size': params['size'],
                'color': params['color'],
                'alpha': params['alpha'],
                'linetype': params['linetype'],
            })
            super().draw_group(
                data, panel_params, coord, ax, length=length, **params)

    @classmethod
    def _calc_ticks(cls, value_range):
        """Calculate appropriate log10 tick marks"""
        lower_log = int(np.floor(value_range[0]))
        upper_log = int(np.ceil(value_range[1])) + 1
        major = cls._calc_ticks_inner(lower_log, upper_log, [1.0])
        middle = cls._calc_ticks_inner(lower_log, upper_log, [0.5])
        minor = cls._calc_ticks_inner(lower_log, upper_log,
                                      [0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
        return major, middle, minor

    @staticmethod
    def _calc_ticks_inner(lower_log, upper_log, marks_at):
        """Calculate log10 tick marks between two logs
        (input is -1..4, not 0.1..10000).
        Marks are set at the percentages defined by marks_at
        ([0..1, ...]])
        """
        result = []
        for l in range(lower_log, upper_log + 1):
            for m in marks_at:
                result.append(10**(l + np.log10(m)))
        return np.log10(result)


class annotation_logticks(annotate):
    """
    Marginal log10 ticks.

    If added to a plot that does not have a log10 axis
    on the respective side, a warning will be issued.

    {usage}

    Parameters
    ----------
    {common_parameters}
    sides : str (default: bl)
        Sides onto which to draw the marks. Any combination
        chosen from the characters ``btlr``, for *bottom*, *top*,
        *left* or *right* side marks. If coord_flip() is used,
        these are the sides *after* the flip.

    length: tuple (default (0.036, 0.0225, 0.012))
        length of the ticks drawn for full / half / tenth
        ticks relative to panel size
    """

    def __init__(self,
                 sides='bl',
                 alpha=1,
                 color='black',
                 size=0.5,
                 linetype='solid',
                 lengths=(0.036, 0.0225, 0.012),
                 **kwargs):
        if len(lengths) != 3:
            raise ValueError(
                "length for annotation_logticks must be a tuple of 3 floats")

        self._annotation_geom = _geom_logticks(sides=sides,
                                               alpha=alpha,
                                               color=color,
                                               size=size,
                                               linetype=linetype,
                                               lengths=lengths,
                                               **kwargs)

    def __radd__(self, gg, inplace=False):
        return self._annotation_geom.__radd__(gg, inplace=inplace)
