from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.text import Text
from six.moves import zip

from .geom import geom
from ..utils import make_iterable_ntimes, to_rgba, suppress
from ..positions import position_nudge


# Note: hjust & vjust are parameters instead of aesthetics
# due to a limitation imposed by MPL
# see: https://github.com/matplotlib/matplotlib/pull/1181
class geom_text(geom):
    DEFAULT_AES = {'alpha': None, 'angle': 0, 'color': 'black',
                   'family': None, 'fontface': 1, 'size': 12,
                   'lineheight': 1.2}
    REQUIRED_AES = {'label', 'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'parse': False, 'hjust': 'center',
                      'vjust': 'center', 'nudge_x': 0, 'nudge_y': 0}

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
    def draw(pinfo, scales, coordinates, ax, **params):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        color = to_rgba(pinfo['color'], pinfo['alpha'])
        # TODO: Deal with the fontface
        # from ggplot2
        # 1 = plain, 2 = bold, 3 = italic, 4 = bold italic
        # "plain", "bold", "italic", "oblique", and "bold.italic"
        pinfo.pop('fontface')

        n = len(x)
        if isinstance(color, tuple):
            color = [color] * n
        labels = make_iterable_ntimes(pinfo['label'], n)
        lineheight = make_iterable_ntimes(pinfo['lineheight'], n)
        size = make_iterable_ntimes(pinfo['size'], n)
        family = make_iterable_ntimes(pinfo['family'], n)
        angle = make_iterable_ntimes(pinfo['angle'], n)

        if params['parse']:
            labels = ['${}$'.format(l) for l in labels]
        items = (x, y, labels, color, family, size, lineheight, angle)
        for x_g, y_g, s, col, fam, sz, lh, ang in zip(*items):
            ax.text(x_g, y_g, s,
                    color=col,
                    family=fam,
                    size=sz,
                    linespacing=lh,
                    verticalalignment=params['vjust'],
                    horizontalalignment=params['hjust'],
                    rotation=ang,
                    zorder=pinfo['zorder'])

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
                   family=data['family'],
                   color=data['color'],
                   rotation=data['angle'],
                   horizontalalignment='center',
                   verticalalignment='center')
        da.add_artist(key)
        return da
