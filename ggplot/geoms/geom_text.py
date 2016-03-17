from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.text import Text

from .geom import geom
from ..utils import to_rgba, suppress
from ..positions import position_nudge


# Note: hjust & vjust are parameters instead of aesthetics
# due to a limitation imposed by MPL
# see: https://github.com/matplotlib/matplotlib/pull/1181
class geom_text(geom):
    DEFAULT_AES = {'alpha': 1, 'angle': 0, 'color': 'black',
                   'size': 11, 'lineheight': 1.2}
    REQUIRED_AES = {'label', 'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'parse': False, 'hjust': 'center',
                      'family': None, 'fontweight': 'bold',
                      'fontstyle': 'normal', 'vjust': 'center',
                      'nudge_x': 0, 'nudge_y': 0}

    def __init__(self, *args, **kwargs):
        nudge_kwargs = {}
        with suppress(KeyError):
            nudge_kwargs['x'] = kwargs['nudge_x']
        with suppress(KeyError):
            nudge_kwargs['y'] = kwargs['nudge_y']
        if nudge_kwargs:
            kwargs['position'] = position_nudge(**nudge_kwargs)
        geom.__init__(self, *args, **kwargs)

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        # Bind color and alpha
        color = to_rgba(data['color'], data['alpha'])

        if isinstance(color, tuple):
            color = [list(color)] * len(data['x'])

        # Parse latex
        if params['parse']:
            data['label'] = ['${}$'.format(l)
                             for l in data['label']]

        # Put all ax.text parameters in dataframe so
        # that each row represents a text instance
        data.rename(columns={'label': 's',
                             'angle': 'rotation',
                             'lineheight': 'linespacing'},
                    inplace=True)
        data['color'] = color
        data['horizontalalignment'] = params['hjust']
        data['verticalalignment'] = params['vjust']
        data['family'] = params['family']
        data['fontweight'] = params['fontweight']
        data['clip_on'] = True

        # 'fill' indicates geom_label so we need an MPL bbox
        draw_label = 'fill' in data
        if draw_label:
            fill = to_rgba(data.pop('fill'), data['alpha'])
            if isinstance(fill, tuple):
                fill = [list(fill)] * len(data['x'])
            data['facecolor'] = fill

            if params['boxstyle'] in ('round', 'round4'):
                boxstyle = '{},pad={},rounding_size={}'.format(
                    params['boxstyle'],
                    params['label_padding'],
                    params['label_r'])
            else:
                boxstyle = '{},pad={}'.format(
                    params['boxstyle'],
                    params['label_padding'])
            bbox = {'linewidth': params['label_size'],
                    'boxstyle': boxstyle}
        else:
            bbox = {}

        # Unwanted
        del data['PANEL']
        del data['group']
        del data['alpha']

        # For labels add a bbox
        for i in range(len(data)):
            kw = data.iloc[i].to_dict()
            if draw_label:
                kw['bbox'] = bbox
                kw['bbox']['edgecolor'] = kw['color']
                kw['bbox']['facecolor'] = kw.pop('facecolor')
            ax.text(**kw)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        key = Text(x=0.5*da.width,
                   y=0.5*da.height,
                   text='a',
                   alpha=data['alpha'],
                   size=data['size'],
                   family=lyr.geom.params['family'],
                   color=data['color'],
                   rotation=data['angle'],
                   horizontalalignment='center',
                   verticalalignment='center')
        da.add_artist(key)
        return da
