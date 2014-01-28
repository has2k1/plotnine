import matplotlib as mpl
import matplotlib.pyplot as plt

from .geom import geom


class geom_rect(geom):
    VALID_AES = ['xmax', 'xmin', 'ymax', 'ymin', 'colour', 'color', 'fill',
                 'linetype', 'size', 'alpha']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        if 'xmin' in layer:
            layer['left'] = layer['xmin']
            del layer['xmin']
        else:
            return

        if 'xmax' in layer:
            xcoords = zip(layer['left'], layer['xmax'])
            width = [xmax - xmin for xmin, xmax in xcoords]
            layer['width'] = width
            del layer['xmax']
        else:
            return

        if 'ymin' in layer:
            layer['bottom'] = layer['ymin']
            del layer['ymin']
        else:
            return

        if 'ymax' in layer:
            ycoords = zip(layer['bottom'], layer['ymax'])
            height = [ymax - ymin for ymin, ymax in ycoords]
            layer['height'] = height
            del layer['ymax']
        else:
            return

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
