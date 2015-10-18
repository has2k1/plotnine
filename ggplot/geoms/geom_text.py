from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
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
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        # Not used by Text
        del pinfo['PANEL']
        del pinfo['group']

        # Bind color and alpha
        color = to_rgba(pinfo['color'], pinfo['alpha'])
        if isinstance(color, tuple):
            color = [color] * len(pinfo['x'])

        # Parse latex
        labels = pinfo.pop('label')
        if params['parse']:
            labels = ['${}$'.format(l) for l in labels]

        # Create ax.text parameters
        pinfo['color'] = color
        pinfo['s'] = labels
        pinfo['linespacing'] = pinfo.pop('lineheight')
        pinfo['rotation'] = pinfo.pop('angle')
        pinfo['horizontalalignment'] = params['hjust']
        pinfo['verticalalignment'] = params['vjust']
        pinfo['family'] = params['family']
        pinfo['fontweight'] = params['fontweight']
        pinfo['clip_on'] = True

        # When fill is present we are creating a label,
        # so we need an MPL bbox
        is_geom_label = 'fill' in pinfo
        if is_geom_label:
            pinfo['facecolor'] = pinfo.pop('fill')
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

        # Put all params in dataframe so that each row
        # represents a text instance & when there is a
        # facecolor we add the bbox
        df = pd.DataFrame(pinfo)
        for i in range(len(df)):
            kw = df[df.columns].iloc[i].to_dict()
            if is_geom_label:
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
