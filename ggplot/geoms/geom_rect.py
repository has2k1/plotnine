import matplotlib as mpl
import matplotlib.pyplot as plt

from .geom import geom


class geom_rect(geom):
    """
    Draw a rectangle on a plot.

    Aesthetics (* - required)
    ----------
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

    VALID_AES = ['xmax', 'xmin', 'ymax', 'ymin', 'colour', 'color', 'fill',
                 'linetype', 'size', 'alpha']
    REQUIRED_AES = ['xmax', 'xmin', 'ymax', 'ymin']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        missing_aes = [aes for aes in self.REQUIRED_AES if aes not in layer]
        if missing_aes:
            msg = 'geom_rect requires the following missing aesthetics: {}'
            raise Exception(msg.format(', '.join(missing_aes)))

        if 'xmin' in layer:
            layer['left'] = layer['xmin']
            del layer['xmin']

        if 'xmax' in layer:
            xcoords = zip(layer['left'], layer['xmax'])
            width = [xmax - xmin for xmin, xmax in xcoords]
            layer['width'] = width
            del layer['xmax']

        if 'ymin' in layer:
            layer['bottom'] = layer['ymin']
            del layer['ymin']

        if 'ymax' in layer:
            ycoords = zip(layer['bottom'], layer['ymax'])
            height = [ymax - ymin for ymin, ymax in ycoords]
            layer['height'] = height
            del layer['ymax']

        if 'colour' in layer:
            layer['edgecolor'] = layer['colour']
            del layer['colour']
            del layer['color']

        if 'color' in layer:
            layer['edgecolor'] = layer['color']
            del layer['color']

        if 'linetype' in layer:
            layer['linestyle'] = layer['linetype']
            del layer['linetype']

        if 'size' in layer:
            layer['linewidth'] = layer['size']
            del layer['size']

        if 'fill' in layer:
            layer['color'] = layer['fill']
            del layer['fill']

        plt.bar(**layer)
