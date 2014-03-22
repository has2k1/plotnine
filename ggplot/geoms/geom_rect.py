
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

    VALID_AES = {'xmax', 'xmin', 'ymax', 'ymin', 'color', 'fill',
                 'linetype', 'size', 'alpha'}
    REQUIRED_AES = {'xmax', 'xmin', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _groups = {'color', 'alpha', 'linetype', 'size'}
    _aes_renames = {'xmin': 'left', 'ymin': 'bottom', 'size': 'linewidth',
                     'linetype': 'linestyle'}

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

        pinfo['edgecolor'] = pinfo.pop('color', '#333333')
        pinfo['color'] = pinfo.pop('fill', '#333333')

        ax.bar(**pinfo)
