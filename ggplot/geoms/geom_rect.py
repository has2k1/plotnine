from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom


class geom_rect(geom):
    """
    Draw a rectangle on a plot.

    Notes
    -----
    geom_rect accepts the following aesthetics (* - required):
    xmax *
    xmin *
    ymax *
    ymin *
    alpha
    colour
    fill
    linetype
    size
    """

    DEFAULT_AES = {'color': '#333333', 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0, 'alpha': None}

    REQUIRED_AES = {'xmax', 'xmin', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'xmin': 'left', 'ymin': 'bottom', 'size': 'linewidth',
                    'linetype': 'linestyle', 'fill': 'facecolor',
                    'color': 'edgecolor'}
    _groups = {'alpha', 'facecolor', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        if isinstance(pinfo['xmax'], list):
            xcoords = zip(pinfo['left'], pinfo['xmax'])
            width = [xmax - xmin for xmin, xmax in xcoords]
        else:
            width = pinfo['xmax'] - pinfo['left']
        pinfo['width'] = width
        del pinfo['xmax']

        if isinstance(pinfo['ymax'], list):
            ycoords = zip(pinfo['bottom'], pinfo['ymax'])
            height = [ymax - ymin for ymin, ymax in ycoords]
        else:
            height = pinfo['ymax'] - pinfo['bottom']
        pinfo['height'] = height
        del pinfo['ymax']

        ax.bar(**pinfo)
