
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

    VALID_AES = ['xmax', 'xmin', 'ymax', 'ymin', 'color', 'fill',
                 'linetype', 'size', 'alpha']
    REQUIRED_AES = ['xmax', 'xmin', 'ymax', 'ymin']

    def plot_layer(self, data, ax):
        groups = {'color', 'alpha', 'linetype', 'size'}
        groups = groups & set(data.columns)
        if groups:
            for name, _data in data.groupby(list(groups)):
                _data = _data.to_dict('list')
                for ae in groups:
                    _data[ae] = _data[ae][0]
                self._plot(_data, ax)
        else:
            _data = data.to_dict('list')
            self._plot(_data, ax)

    def _plot(self, layer, ax):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
        layer.update(self.manual_aes)

        missing_aes = [aes for aes in self.REQUIRED_AES if aes not in layer]
        if missing_aes:
            msg = 'geom_rect requires the following missing aesthetics: {}'
            raise Exception(msg.format(', '.join(missing_aes)))

        if 'xmin' in layer:
            layer['left'] = layer['xmin']
            del layer['xmin']

        if 'xmax' in layer:
            if isinstance(layer['xmax'], list):
                xcoords = zip(layer['left'], layer['xmax'])
                width = [xmax - xmin for xmin, xmax in xcoords]
            else:
                width = layer['xmax'] - layer['left']
            layer['width'] = width
            del layer['xmax']

        if 'ymin' in layer:
            layer['bottom'] = layer['ymin']
            del layer['ymin']

        if 'ymax' in layer:
            if isinstance(layer['ymax'], list):
                ycoords = zip(layer['bottom'], layer['ymax'])
                height = [ymax - ymin for ymin, ymax in ycoords]
            else:
                height = layer['ymax'] - layer['bottom']
            layer['height'] = height
            del layer['ymax']

        if 'color' in layer:
            layer['edgecolor'] = layer['color']
            del layer['color']
        else:
            layer['edgecolor'] = '#333333'

        if 'linetype' in layer:
            layer['linestyle'] = layer['linetype']
            del layer['linetype']

        if 'size' in layer:
            layer['linewidth'] = layer['size']
            del layer['size']

        if 'fill' in layer:
            layer['color'] = layer['fill']
            del layer['fill']
        else:
            layer['color'] = '#333333'

        ax.bar(**layer)
