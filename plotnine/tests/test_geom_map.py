import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import (
    Point,
    Polygon,
    LineString,
    MultiPoint,
    MultiPolygon,
    MultiLineString
)

from plotnine import ggplot, aes, geom_map, labs, theme, facet_wrap

_theme = theme(subplots_adjust={'right': 0.85})


def test_geometries():
    # Points
    points = [Point(0, 0), Point(0, 1), Point(1, 1), Point(1, 0)]
    point_names = [f'point{i}' for i in range(len(points))]
    df_point = GeoDataFrame({'names': point_names, 'geometry': points})

    # LineString
    n = 5
    x = np.repeat(np.linspace(0, 1, n), 2)
    y = np.tile([0.375, 0.625], n)
    lines = [LineString(list(zip(x, y)))]
    df_line = GeoDataFrame({'name': ['line1'], 'geometry': lines})

    # MultiLineString
    n = 5
    x = np.repeat(np.linspace(0, 1, n), 2)
    y = np.tile([0.375, 0.625], n) + 1
    line = list(zip(x, y))
    mlines = [MultiLineString([line[:5], line[5:]])]
    df_multiline = GeoDataFrame({'name': 'multiline1', 'geometry': mlines})

    #  Polygon
    polygons = [
        Polygon([(.25, -.25), (.25, .25), (.75, .25), (.75, -.25)]),
        Polygon([(.25, .75), (.75, .75), (.5, 1.25)])
    ]
    names = [f'polygon{i}' for i in range(len(polygons))]
    df_polygon = GeoDataFrame({'name': names, 'geometry': polygons})

    p = (ggplot()
         + aes(fill='geometry.bounds.miny')
         + geom_map(df_polygon)
         + geom_map(df_point, size=4)
         + geom_map(df_line, size=2)
         + geom_map(df_multiline, size=2)
         + labs(fill='miny')
         )

    assert p + _theme == 'geometries'


def test_multipolygon():
    # 2 MultiPolygon
    # 1. 4 Solid Squares
    # 2. 4 Squares with holes (to the upper-right of each of
    #    the squares in 1)
    length = 0.5
    centers = np.array([[1, 1], [1, 2], [2, 2], [2, 1]])
    corners = np.array([[-1, -1], [-1, 1], [1, 1], [1, -1]])
    shift = corners * (length/2)
    shift_holes = corners * (length/4)
    mpolygons = [
        MultiPolygon([(c + shift, None) for c in centers]),
        MultiPolygon([
            (c + length + shift, [c + length + shift_holes])
            for c in centers
        ])
    ]
    names = [f'mpolygon{i}' for i in range(len(mpolygons))]
    df = GeoDataFrame({'name': names, 'geometry': mpolygons})
    p = (ggplot()
         + aes(fill='geometry.bounds.miny')
         + geom_map(df)
         + labs(fill='miny')
         + theme(aspect_ratio=1)
         )

    assert p + _theme == 'multipolygon'


def test_multipoint():
    mpoints = [
        MultiPoint([[0.0, 0.0], [1.0, 1.0]]),
        MultiPoint([[0.0, 1.0], [1.0, 2.0]])
    ]

    mpoint_names = [f'mpoint{i}' for i in range(len(mpoints))]
    df = GeoDataFrame({'names': mpoint_names, 'geometry': mpoints})

    p = (ggplot()
         + aes(fill='geometry.bounds.miny')
         + geom_map(df, size=5, color='None')
         + labs(fill='miny')
         )
    assert p + _theme == 'multipoint'


def test_facet_wrap():
    #  Polygon
    polygons = [
        Polygon([(.25, -.25), (.25, .25), (.75, .25), (.75, -.25)]),
        Polygon([(.25, .75), (.75, .75), (.5, 1.25)])
    ]
    names = [f'polygon{i}' for i in range(len(polygons))]
    df_polygon = GeoDataFrame({
        'name': names,
        'geometry': polygons,
        'shape': ['rectangle', 'triangle']
    })

    p = (ggplot()
         + aes(fill='geometry.bounds.miny')
         + geom_map(df_polygon)
         + facet_wrap('shape')
         + labs(fill='miny')
         )
    assert p + _theme == 'facet_wrap'
