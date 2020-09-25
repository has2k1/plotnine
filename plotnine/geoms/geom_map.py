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
                      'na_rm': False}
    REQUIRED_AES = {'geometry'}
    legend_geom = 'polygon'

    def __init__(self, mapping=None, data=None, **kwargs):
        if not HAS_GEOPANDAS:
            raise PlotnineError(
                "geom_map requires geopandas. "
                "Please install geopandas."
            )
        geom.__init__(self, mapping, data, **kwargs)
        # Almost all geodataframes loaded from shapefiles
        # have a geometry column.
        if 'geometry' not in self.mapping:
            self.mapping['geometry'] = 'geometry'

    def setup_data(self, data):
        if not len(data):
            return data

        # Remove any NULL geometries, and remember
        # All the non-Null shapes in a shapefile are required to be
        # of the same shape type.
        bool_idx = np.array([g is not None for g in data['geometry']])
        if not np.all(bool_idx):
            data = data.loc[bool_idx]

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

        data = pd.concat([data, bounds], axis=1)
        return data

    def draw_panel(self, data, panel_params, coord, ax, **params):
        if not len(data):
            return data

        data.loc[data['color'].isnull(), 'color'] = 'none'
        data.loc[data['fill'].isnull(), 'fill'] = 'none'
        data['fill'] = to_rgba(data['fill'], data['alpha'])

        geom_type = data.geometry.iloc[0].geom_type
        if geom_type in ('Polygon', 'MultiPolygon'):
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
        elif geom_type == 'Point':
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
        elif geom_type in ('LineString', 'MultiLineString'):
            data['size'] *= SIZE_FACTOR
            data['color'] = to_rgba(data['color'], data['alpha'])
            segments = []
            for g in data['geometry']:
                if g.geom_type == 'LineString':
                    segments.append(g.coords)
                else:
                    segments.extend(_g.coords for _g in g.geoms)

            coll = LineCollection(
                segments,
                edgecolor=data['color'],
                linewidth=data['size'],
                linestyle=data['linetype'],
                zorder=params['zorder'])
            ax.add_collection(coll)
        else:
            raise TypeError(f"Could not plot geometry of type '{geom_type}'")
