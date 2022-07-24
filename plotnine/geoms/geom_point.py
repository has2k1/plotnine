import numpy as np
import matplotlib.lines as mlines

from ..utils import to_rgba, SIZE_FACTOR
from ..doctools import document
from ..scales.scale_shape import FILLED_SHAPES, UNFILLED_SHAPES
from .geom import geom


@document
class geom_point(geom):
    """
    Plot points (Scatter plot)

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'shape': 'o', 'size': 1.5, 'stroke': 0.5}
    REQUIRED_AES = {'x', 'y'}
    NON_MISSING_AES = {'color', 'shape', 'size'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, **params)

    @classmethod
    def draw_group(cls, data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params)
        units = 'shape'
        for _, udata in data.groupby(units, dropna=False):
            udata.reset_index(inplace=True, drop=True)
            cls.draw_unit(udata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_unit(data, panel_params, coord, ax, **params):
        # Our size is in 'points' while scatter wants
        # 'points^2'. The stroke is outside. And pi
        # gives a large enough scaling factor
        # All other sizes for which the MPL units should
        # be in points must scaled using sqrt(pi)
        size = ((data['size']+data['stroke'])**2)*np.pi
        stroke = data['stroke'] * SIZE_FACTOR
        color = to_rgba(data['color'], data['alpha'])
        shape = data.loc[0, 'shape']

        # It is common to forget that scatter points are
        # filled and slip-up by manually assigning to the
        # color instead of the fill. We forgive.
        if shape in FILLED_SHAPES:
            if all(c is None for c in data['fill']):
                fill = color
            else:
                fill = to_rgba(data['fill'], data['alpha'])
        elif shape in UNFILLED_SHAPES:
            fill = color
            color = None
        else:
            raise ValueError(
                f"geom_point got an unknown shape: {shape}"
            )

        ax.scatter(
            x=data['x'],
            y=data['y'],
            s=size,
            facecolor=fill,
            edgecolor=color,
            linewidth=stroke,
            marker=shape,
            zorder=params['zorder'],
            rasterized=params['raster']
        )

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a point in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        if data['fill'] is None:
            data['fill'] = data['color']

        size = (data['size']+data['stroke'])*SIZE_FACTOR
        stroke = data['stroke'] * SIZE_FACTOR

        key = mlines.Line2D(
            [0.5*da.width],
            [0.5*da.height],
            alpha=data['alpha'],
            marker=data['shape'],
            markersize=size,
            markerfacecolor=data['fill'],
            markeredgecolor=data['color'],
            markeredgewidth=stroke
        )
        da.add_artist(key)
        return da
