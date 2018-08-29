import numpy as np
import shapefile
from geopandas import GeoDataFrame

from plotnine import ggplot, aes, geom_map, labs, theme

_theme = theme(subplots_adjust={'right': 0.85})


def _create_test_input_files(test_file):
    w = shapefile.Writer()
    w.field('name', 'C')

    # Points
    w.point(0, 0)
    w.record('point1')

    w.point(0, 1)
    w.record('point2')

    w.point(1, 1)
    w.record('point3')

    w.point(1, 0)
    w.record('point4')

    # Polygons
    w.poly(parts=[
        [[.25, -.25], [.25, .25], [.75, .25], [.75, -.25]],
    ])
    w.record('polygon1')

    w.poly(parts=[
        [[.25, .75], [.75, .75], [.5, 1.25]]
    ])
    w.record('polygon2')

    # Lines
    n = 5
    x = np.repeat(np.linspace(0, 1, n), 2)
    y = np.tile([0.375, 0.625], n)
    w.line(parts=[
        list(zip(x, y))
    ])
    w.record('line1')

    w.save(test_file)


def test_geometries(tmpdir):
    test_file = '{}/test_file.shp'.format(tmpdir)
    _create_test_input_files(test_file)

    df = GeoDataFrame.from_file(test_file)
    p = (ggplot(df)
         + aes(fill='geometry.bounds.miny')
         + geom_map()
         + geom_map(draw='Point', size=4)
         + geom_map(draw='LineString', size=2)
         + labs(fill='miny')
         )

    assert p + _theme == 'geometries'
