from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_raises

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

from ggplot import *
from ggplot.exampledata import diamonds


@cleanup
def test_geom_rect():
    df = pd.DataFrame({
        'xmin': [1,3,5],
        'xmax': [2, 3.5, 7],
        'ymin': [1, 4, 6],
        'ymax': [5, 5, 9],
        'fill': ['blue', 'red', 'green'],
        'quality': ['good', 'bad', 'ugly'],
        'alpha': [0.1, 0.5, 0.9],
        'texture': ['hard', 'soft', 'medium']})
    p = ggplot(df, aes(xmin='xmin', xmax='xmax', ymin='ymin', ymax='ymax',
               colour='quality', fill='fill', alpha='alpha',
               linetype='texture'))
    p += geom_rect(size=5)
    assert_same_ggplot(p, 'geom_rect')

    p = ggplot(df, aes(x='xmin', y='ymin'))
    p += geom_point(size=100, colour='red', alpha=0.5)
    p += geom_rect(aes(fill='fill', xmin='xmin', xmax='xmax', ymin=0,
                   ymax='ymax'), alpha=0.1)
    assert_same_ggplot(p, 'geom_rect_with_point')


def test_geom_rect_missing_req_aes():
    with assert_raises(Exception):
        print(ggplot(diamonds, aes(x=x, y=y)) + geom_point() + geom_rect())
