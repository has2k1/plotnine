import pandas as pd
import numpy as np
from matplotlib.collections import PatchCollection, LineCollection
from descartes.patch import PolygonPatch

try:
    import geopandas  # noqa: F401
except ImportError:
    HAS_GEOPANDAS = False
else:
    HAS_GEOPANDAS = True

from ..doctools import document
from ..exceptions import PlotnineError
from ..utils import to_rgba, SIZE_FACTOR
from .geom import geom
from .geom_point import geom_point


@document
class geom_map(geom):
    """
    Draw map feature

    The map feature are drawn without any special projections.

    {usage}

    Parameters
    ----------
    {common_parameters}
    draw : str in ``['Polygon', 'Point', 'LineString']``
        What geometry types to draw. Note that *Polygon*
        includes MultiPolygon type.

    Notes
    -----
    This geom is best suited for plotting a shapefile read into
    geopandas dataframe. The dataframe should have a ``geometry``
    column.
    """
    DEFAULT_AES = {'alpha': 1, 'color': '#111111', 'fill': '#333333',
                   'linetype': 'solid', 'shape': 'o', 'size': 0.5,
                   'stroke': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'draw': 'Polygon', 'na_rm': False}
    REQUIRED_AES = {'geometry'}
    legend_geom = 'polygon'

    def __init__(self, *args, **kwargs):
        if not HAS_GEOPANDAS:
            raise PlotnineError(
                "geom_map requires geopandas. "
                "Please install geopandas."
            )
        geom.__init__(self, *args, **kwargs)
        # Almost all geodataframes loaded from shapefiles
        # have a geometry column.
        if 'geometry' not in self.mapping:
            self.mapping['geometry'] = 'geometry'

    def setup_data(self, data):
        draw = self.params['draw']
        _type = data.geometry.geom_type
        if draw == 'Polygon':
            data = data[(_type == 'Polygon') | (_type == 'MultiPolygon')]
        elif draw == 'Point':
            data = data[_type == 'Point']
        elif draw == 'LineString':
            data = data[_type == 'LineString']

        if not len(data):
            return data

        # Add polygon limits. Scale training uses them
        try:
            bounds = data['geometry'].bounds
        except AttributeError:
            # The geometry is not a GeoSeries
            # Bounds calculation is extracted from
            # geopandas.base.GeoPandasBase.bounds
            bounds = pd.DataFrame(
                np.array([x.bounds for x in data['geometry']]),
                columns=['xmin', 'ymin', 'xmax', 'ymax'],
                index=data.index)
        else:
            bounds.rename(
                columns={
                    'minx': 'xmin',
                    'maxx': 'xmax',
                    'miny': 'ymin',
                    'maxy': 'ymax'
                },
                inplace=True)

        data = pd.concat([data, bounds], axis=1, copy=False)
        return data

    def draw_panel(self, data, panel_params, coord, ax, **params):
        _loc = data.columns.get_loc
        cidx = data.index[data['color'].isnull()]
        fidx = data.index[data['fill'].isnull()]
        data.iloc[cidx, _loc('color')] = 'none'
        data.iloc[fidx, _loc('fill')] = 'none'
        data['fill'] = to_rgba(data['fill'], data['alpha'])

        if params['draw'] == 'Polygon':
            data['size'] *= SIZE_FACTOR
            patches = [PolygonPatch(g) for g in data['geometry']]
            coll = PatchCollection(
                patches,
                edgecolor=data['color'],
                facecolor=data['fill'],
                linestyle=data['linetype'],
                linewidth=data['size'],
                zorder=params['zorder'],
            )
            ax.add_collection(coll)
        elif params['draw'] == 'Point':
            # Extract point coordinates from shapely geom
            # and plot with geom_point
            arr = np.array([list(g.coords)[0] for g in data['geometry']])
            data['x'] = arr[:, 0]
            data['y'] = arr[:, 1]
            for _, gdata in data.groupby('group'):
                gdata.reset_index(inplace=True, drop=True)
                gdata.is_copy = None
                geom_point.draw_group(
                    gdata, panel_params, coord, ax, **params)
        elif params['draw'] == 'LineString':
            data['size'] *= SIZE_FACTOR
            data['color'] = to_rgba(data['color'], data['alpha'])
            segments = [list(g.coords) for g in data['geometry']]
            coll = LineCollection(
                segments,
                edgecolor=data['color'],
                linewidth=data['size'],
                linestyle=data['linetype'],
                zorder=params['zorder'])
            ax.add_collection(coll)
