
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
    _translations = {'xmin': 'left', 'ymin': 'bottom', 'size': 'linewidth'}

    def plot(self, layer, ax):
        if isinstance(layer['xmax'], list):
            xcoords = zip(layer['left'], layer['xmax'])
            width = [xmax - xmin for xmin, xmax in xcoords]
        else:
            width = layer['xmax'] - layer['left']
        layer['width'] = width
        del layer['xmax']

        if isinstance(layer['ymax'], list):
            ycoords = zip(layer['bottom'], layer['ymax'])
            height = [ymax - ymin for ymin, ymax in ycoords]
        else:
            height = layer['ymax'] - layer['bottom']
        layer['height'] = height
        del layer['ymax']

        layer['edgecolor'] = layer.pop('color', '#333333')
        layer['color'] = layer.pop('fill', '#333333')

        ax.bar(**layer)
