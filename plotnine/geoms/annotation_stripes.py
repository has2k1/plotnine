from itertools import islice, cycle

import pandas as pd
import numpy as np

from .geom import geom
from .geom_rect import geom_rect
from .annotate import annotate
from ..coords import coord_flip


class annotation_stripes(annotate):
    """
    Alternating stripes, centered around each label.

    Useful as a background for geom_jitter.

    Parameters
    ----------
    fill : list-like
        List of colors for the strips. The default  is
        `("#AAAAAA", "#CCCCCC")`
    fill_range: bool
        If True, the more stripes are created to cover the
        edges of the range. This may be desired for discrete
        scales.
    direction : 'vertical' or 'horizontal'
        Orientation of the stripes
    extend : tuple
        Range of the stripes. The default is (0, 1), top to bottom.
        The values should be in the range [0, 1].
    **kwargs : dict
        Other aesthetic parameters for the rectangular stripes.
        They include; *alpha*, *color*, *linetype*, and *size*.
    """

    def __init__(self, fill=('#AAAAAA', '#CCCCCC'), fill_range=False,
                 direction='vertical', extend=(0, 1), **kwargs):
        allowed = ('vertical', 'horizontal')
        if direction not in allowed:
            raise ValueError(
                "direction must be one of {}".format(allowed))
        self._annotation_geom = _geom_stripes(
            fill=fill, fill_range=fill_range, extend=extend,
            direction=direction, **kwargs)


class _geom_stripes(geom):

    DEFAULT_AES = {}
    REQUIRED_AES = set()
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'color': None,
                      'fill': ('#AAAAAA', '#CCCCCC'),
                      'linetype': 'solid', 'size': 1, 'alpha': 0.5,
                      'direction': 'vertical', 'extend': (0, 1),
                      'fill_range': False}
    legend_geom = "polygon"

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        extend = params['extend']
        fill_range = params['fill_range']
        direction = params['direction']

        # Range
        if direction == 'vertical':
            axis, other_axis = 'x', 'y'
        else:
            axis, other_axis = 'y', 'x'

        if isinstance(coord, coord_flip):
            axis, other_axis = other_axis, axis

        breaks = getattr(panel_params, axis).breaks
        range = getattr(panel_params, axis).range
        other_range = getattr(panel_params, other_axis).range

        # Breaks along the width
        n_stripes = len(breaks)
        diff = np.diff(breaks)
        step = diff[0]
        equal_spaces = np.all(diff == step)
        if not equal_spaces:
            raise ValueError(
                "The major breaks are not equally spaced. "
                "We cannot create stripes."
            )

        deltas = np.array([step/2] * n_stripes)
        xmin = breaks - deltas
        xmax = breaks + deltas
        if fill_range:
            if range[0] < breaks[0]:
                n_stripes += 1
                xmax = np.insert(xmax, 0, xmin[0])
                xmin = np.insert(xmin, 0, range[0])
            if range[1] > breaks[1]:
                n_stripes += 1
                xmin = np.append(xmin, xmax[-1])
                xmax = np.append(xmax, range[1])

        # Height
        full_height = other_range[1] - other_range[0]
        ymin = other_range[0] + full_height * extend[0]
        ymax = other_range[0] + full_height * extend[1]
        fill = list(islice(cycle(params['fill']), n_stripes))

        if direction != 'vertical':
            xmin, xmax, ymin, ymax = ymin, ymax, xmin, xmax

        data = pd.DataFrame({
            'xmin': xmin,
            'xmax': xmax,
            'ymin': ymin,
            'ymax': ymax,
            'fill': fill,
            'alpha': params['alpha'],
            'color': params['color'],
            'linetype': params['linetype'],
            'size': params['size']
        })

        return geom_rect.draw_group(data, panel_params, coord, ax, **params)
