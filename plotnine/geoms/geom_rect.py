from matplotlib.collections import PolyCollection
import numpy as np
import pandas as pd

from ..utils import to_rgba, SIZE_FACTOR
from ..doctools import document
from .geom import geom
from .geom_polygon import geom_polygon


@document
class geom_rect(geom):
    """
    Rectangles

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {'color': None, 'fill': '#595959',
                   'linetype': 'solid', 'size': 0.5, 'alpha': 1}
    REQUIRED_AES = {'xmax', 'xmin', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    legend_geom = 'polygon'

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        if not coord.is_linear:
            data = _rectangles_to_polygons(data)
            for _, gdata in data.groupby('group'):
                gdata.reset_index(inplace=True, drop=True)
                geom_polygon.draw_group(
                    gdata, panel_params, coord, ax, **params)
        else:
            self.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params, munch=True)
        data['size'] *= SIZE_FACTOR
        verts = [None] * len(data)

        limits = zip(data['xmin'], data['xmax'],
                     data['ymin'], data['ymax'])

        for i, (l, r, b, t) in enumerate(limits):
            verts[i] = [(l, b), (l, t), (r, t), (r, b)]

        fill = to_rgba(data['fill'], data['alpha'])
        color = data['color']

        # prevent unnecessary borders
        if all(color.isnull()):
            color = 'none'

        col = PolyCollection(
            verts,
            facecolors=fill,
            edgecolors=color,
            linestyles=data['linetype'],
            linewidths=data['size'],
            transOffset=ax.transData,
            zorder=params['zorder'])
        ax.add_collection(col)


def _rectangles_to_polygons(df):
    """
    Convert rect data to polygons

    Paramters
    ---------
    df : dataframe
        Dataframe with *xmin*, *xmax*, *ymin* and *ymax* columns,
        plus others for aesthetics ...

    Returns
    -------
    data : dataframe
        Dataframe with *x* and *y* columns, plus others for
        aesthetics ...
    """
    n = len(df)

    # Helper indexing arrays
    xmin_idx = np.tile([True, True, False, False], n)
    xmax_idx = ~xmin_idx
    ymin_idx = np.tile([True, False, False, True], n)
    ymax_idx = ~ymin_idx

    # There are 2 x and 2 y values for each of xmin, xmax, ymin & ymax
    # The positions are as layed out in the indexing arrays
    # x and y values
    x = np.empty(n*4)
    y = np.empty(n*4)
    x[xmin_idx] = df['xmin'].repeat(2)
    x[xmax_idx] = df['xmax'].repeat(2)
    y[ymin_idx] = df['ymin'].repeat(2)
    y[ymax_idx] = df['ymax'].repeat(2)

    # Aesthetic columns and others
    other_cols = df.columns.difference(
        ['x', 'y', 'xmin', 'xmax', 'ymin', 'ymax'])
    d = {col: np.repeat(df[col].values, 4) for col in other_cols}
    data = pd.DataFrame({
        'x': x,
        'y': y,
        **d
    })
    return data
