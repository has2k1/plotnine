from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import matplotlib.lines as mlines
from matplotlib.patches import Rectangle

from ..doctools import document
from ..utils import make_iterable_ntimes, to_rgba, copy_missing_columns
from ..utils import resolution, SIZE_FACTOR
from .geom_point import geom_point
from .geom_segment import geom_segment
from .geom_crossbar import geom_crossbar
from .geom import geom


@document
class geom_boxplot(geom):
    """
    Box and whiskers plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    outlier_alpha : float, optional (default: 1)
        Transparency of the outlier points.
    outlier_color : str or tuple, optional (default: None)
        Color of the outlier points.
    outlier_shape : str, optional (default: o)
        Shape of the outlier points.
    outlier_size : float, optional (default: 1.5)
        Size of the outlier points.
    outlier_stroke : float, optional (default: 0.5)
        Stroke-size of the outlier points.
    notch : bool, optional (default: False)
        Whether the boxes should have a notch.
    varwidth : bool, optional (default: False)
        If :py:`True`, boxes are drawn with widths proportional to
        the square-roots of the number of observations in the
        groups.
    notchwidth : float, optional (default: 0.5)
        Width of notch relative to the body width.
    fatten : float, optional (default: 2)
        A multiplicative factor used to increase the size of the
        middle bar across the box.

    {aesthetics}
    """
    DEFAULT_AES = {'alpha': 1, 'color': '#333333', 'fill': 'white',
                   'linetype': 'solid', 'shape': 'o', 'size': 0.5,
                   'weight': 1}
    REQUIRED_AES = {'x', 'lower', 'upper', 'middle', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'boxplot', 'position': 'dodge',
                      'na_rm': False,
                      'outlier_alpha': 1, 'outlier_color': None,
                      'outlier_shape': 'o', 'outlier_size': 1.5,
                      'outlier_stroke': 0.5, 'notch': False,
                      'varwidth': False, 'notchwidth': 0.5,
                      'fatten': 2}

    def setup_data(self, data):
        if 'width' not in data:
            if 'width' in self.params and self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        # min and max outlier values
        omin = [np.min(lst) if len(lst) else +np.inf
                for lst in data['outliers']]
        omax = [np.max(lst) if len(lst) else -np.inf
                for lst in data['outliers']]

        data['ymin_final'] = np.min(np.column_stack(
            [data['ymin'], omin]), axis=1)
        data['ymax_final'] = np.max(np.column_stack(
            [data['ymax'], omax]), axis=1)

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
    def draw_group(data, panel_params, coord, ax, **params):
        def flat(*args):
            """Flatten list-likes"""
            return np.hstack(args)

        common_columns = ['color', 'size', 'linetype',
                          'fill', 'group', 'alpha', 'shape']
        # whiskers
        whiskers = pd.DataFrame({
            'x': flat(data['x'], data['x']),
            'y': flat(data['upper'], data['lower']),
            'yend': flat(data['ymax'], data['ymin'])})
        whiskers['xend'] = whiskers['x']
        copy_missing_columns(whiskers, data[common_columns])

        # box
        box_columns = ['xmin', 'xmax', 'lower', 'middle', 'upper']
        box = data[common_columns + box_columns].copy()
        box.rename(columns={'lower': 'ymin',
                            'middle': 'y',
                            'upper': 'ymax'},
                   inplace=True)

        # notch
        if params['notch']:
            box['ynotchlower'] = data['notchlower']
            box['ynotchupper'] = data['notchupper']

        # outliers
        num_outliers = len(data['outliers'].iloc[0])
        if num_outliers:
            def outlier_value(param):
                oparam = 'outlier_{}'.format(param)
                if params[oparam] is not None:
                    return params[oparam]
                return data[param].iloc[0]

            outliers = pd.DataFrame({
                'y': data['outliers'].iloc[0],
                'x': make_iterable_ntimes(data['x'][0],
                                          num_outliers),
                'fill': [None]*num_outliers})
            outliers['alpha'] = outlier_value('alpha')
            outliers['color'] = outlier_value('color')
            outliers['shape'] = outlier_value('shape')
            outliers['size'] = outlier_value('size')
            outliers['stroke'] = outlier_value('stroke')
            geom_point.draw_group(outliers, panel_params,
                                  coord, ax, **params)

        # plot
        geom_segment.draw_group(whiskers, panel_params,
                                coord, ax, **params)
        geom_crossbar.draw_group(box, panel_params,
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
        data['size'] *= SIZE_FACTOR

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
