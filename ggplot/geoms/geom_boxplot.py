from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import matplotlib.lines as mlines
from matplotlib.patches import Rectangle

from ..scales.utils import resolution
from ..utils import make_iterable_ntimes, to_rgba
from .geom_point import geom_point
from .geom_segment import geom_segment
from .geom_crossbar import geom_crossbar
from .geom import geom


class geom_boxplot(geom):
    DEFAULT_AES = {'alpha': 1, 'color': '#333333', 'fill': 'white',
                   'linetype': 'solid', 'shape': 'o', 'size': 1,
                   'weight': 1}
    REQUIRED_AES = {'x', 'lower', 'upper', 'middle', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'boxplot', 'position': 'dodge',
                      'outlier_alpha': 1, 'outlier_color': None,
                      'outlier_shape': 'o', 'outlier_size': 5,
                      'outlier_stroke': 0, 'notch': False,
                      'varwidth': False, 'notchwidth': 0.5}

    def setup_data(self, data):
        if 'width' not in data:
            if 'width' in self.params and self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        # if varwidth not requested or not available, don't use it
        if ('varwidth' not in self.params or
                not self.params['varwidth'] or
                'relvarwidth' not in data):
            data['xmin'] = data['x'] - data['width']/2
            data['xmax'] = data['x'] + data['width']/2
        else:
            # make relvarwidth relative to the size of the
            # largest group
            data['relvarwidth'] /= data['relvarwidth'].max()
            data['xmin'] = data['x'] - data['relvarwidth']*data['width']/2
            data['xmax'] = data['x'] + data['relvarwidth']*data['width']/2
            del data['relvarwidth']

        del data['width']

        return data

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):

        def subdict(keys):
            d = {}
            for key in keys:
                d[key] = deepcopy(pinfo[key])
            return d

        common = subdict(('color', 'size', 'linetype',
                          'fill', 'group', 'alpha',
                          'zorder'))

        whiskers = subdict(('x',))
        whiskers.update(deepcopy(common))
        whiskers['x'] = whiskers['x'] * 2
        whiskers['xend'] = whiskers['x']
        whiskers['y'] = pinfo['upper'] + pinfo['lower']
        whiskers['yend'] = pinfo['ymax'] + pinfo['ymin']

        box = subdict(('xmin', 'xmax', 'lower', 'middle', 'upper'))
        box.update(deepcopy(common))
        box['ymin'] = box.pop('lower')
        box['y'] = box.pop('middle')
        box['ymax'] = box.pop('upper')
        box['notchwidth'] = params['notchwidth']
        if params['notch']:
            box['ynotchlower'] = pinfo['notchlower']
            box['ynotchupper'] = pinfo['notchupper']

        if 'outliers' in pinfo and len(pinfo['outliers'][0]):
            outliers = subdict(('alpha', 'zorder'))

            def outlier_value(param):
                oparam = 'outlier_{}'.format(param)
                if params[oparam] is not None:
                    return params[oparam]
                return pinfo[param]

            outliers['y'] = pinfo['outliers'][0]
            outliers['x'] = make_iterable_ntimes(pinfo['x'][0],
                                                 len(outliers['y']))
            outliers['alpha'] = outlier_value('alpha')
            outliers['color'] = outlier_value('color')
            outliers['fill'] = None
            outliers['shape'] = outlier_value('shape')
            outliers['size'] = outlier_value('size')
            outliers['stroke'] = outlier_value('stroke')
            geom_point.draw_group(outliers, panel_scales,
                                  coord, ax, **params)

        geom_segment.draw_group(whiskers, panel_scales,
                                coord, ax, **params)
        params['fatten'] = geom_crossbar.DEFAULT_PARAMS['fatten']
        geom_crossbar.draw_group(box, panel_scales,
                                 coord, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a rectangle in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        # box
        facecolor = to_rgba(data['fill'], data['alpha'])
        if facecolor is None:
            facecolor = 'none'

        kwargs = dict(
           linestyle=data['linetype'],
           linewidth=data['size'])

        box = Rectangle((da.width*.125, da.height*.25),
                        width=da.width*.75,
                        height=da.height*.5,
                        facecolor=facecolor,
                        edgecolor=data['color'],
                        capstyle='projecting',
                        antialiased=False,
                        **kwargs)
        da.add_artist(box)

        kwargs['solid_capstyle'] = 'butt'
        kwargs['color'] = data['color']
        # middle strike through
        strike = mlines.Line2D([da.width*.125, da.width*.875],
                               [da.height*.5, da.height*.5],
                               **kwargs)
        da.add_artist(strike)

        # whiskers
        top = mlines.Line2D([da.width*.5, da.width*.5],
                            [da.height*.75, da.height*.9],
                            **kwargs)
        da.add_artist(top)

        bottom = mlines.Line2D([da.width*.5, da.width*.5],
                               [da.height*.25, da.height*.1],
                               **kwargs)
        da.add_artist(bottom)
        return da
