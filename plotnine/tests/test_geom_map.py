import numpy as np
import shapefile
from geopandas import GeoDataFrame

from plotnine import ggplot, aes, geom_map, labs, theme, facet_wrap

_theme = theme(subplots_adjust={'right': 0.85})


def _point_file(test_file):
    with shapefile.Writer(test_file, shapefile.POINT) as shp:
        shp.field('name', 'C')

        shp.point(0, 0)
        shp.record('point1')

        shp.point(0, 1)
        shp.record('point2')

        shp.point(1, 1)
        shp.record('point3')

        shp.point(1, 0)
        shp.record('point4')


def _polygon_file(test_file):
    with shapefile.Writer(test_file, shapefile.POLYGON) as shp:
        shp.field('name', 'C')

        shp.poly([
            [[.25, -.25], [.25, .25], [.75, .25], [.75, -.25]],
        ])
        shp.record('polygon1')

        shp.poly([
            [[.25, .75], [.75, .75], [.5, 1.25]]
        ])
        shp.record('polygon2')


def _polyline_file(test_file):
    with shapefile.Writer(test_file, shapefile.POLYLINE) as shp:
        shp.field('name', 'C')

        n = 5
        x = np.repeat(np.linspace(0, 1, n), 2)
        y = np.tile([0.375, 0.625], n)
        shp.line([list(zip(x, y))])
        shp.record('line1')


def _polylinem_file(test_file):
    with shapefile.Writer(test_file, shapefile.POLYLINEM) as shp:
        shp.field('name', 'C')

        n = 5
        x = np.repeat(np.linspace(0, 1, n), 2)
        y = np.tile([0.375, 0.625], n) + 1
        line = list(zip(x, y))
        shp.linem([line[:5], line[5:]])
        shp.record('linem1')


def test_geometries(tmpdir):
    point_file = '{}/test_file_point.shp'.format(tmpdir)
    polygon_file = '{}/test_file_polygon.shp'.format(tmpdir)
    polyline_file = '{}/test_file_polyline.shp'.format(tmpdir)
    polylinem_file = '{}/test_file_polylinem.shp'.format(tmpdir)

    _point_file(point_file)
    _polygon_file(polygon_file)
    _polyline_file(polyline_file)
    _polylinem_file(polylinem_file)

    df_point = GeoDataFrame.from_file(point_file)
    df_polygon = GeoDataFrame.from_file(polygon_file)
    df_polyline = GeoDataFrame.from_file(polyline_file)
    df_polylinem = GeoDataFrame.from_file(polylinem_file)

    p = (ggplot()
         + aes(fill='geometry.bounds.miny')
         + geom_map(df_polygon)
         + geom_map(df_point, size=4)
         + geom_map(df_polyline, size=2)
         + geom_map(df_polylinem, size=2)
         + labs(fill='miny')
         )

    assert p + _theme == 'geometries'


def test_facet_wrap(tmpdir):
    polygon_file = '{}/test_file_polygon.shp'.format(tmpdir)
    _polygon_file(polygon_file)

    df_polygon = GeoDataFrame.from_file(polygon_file)
    df_polygon['shape'] = ['rectangle', 'triangle']

    p = (ggplot()
         + aes(fill='geometry.bounds.miny')
         + geom_map(df_polygon)
         + facet_wrap('shape')
         + labs(fill='miny')
         )
    assert p + _theme == 'facet_wrap'
