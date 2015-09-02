from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from nose.tools import (assert_equal, assert_is, assert_is_not,
                        assert_raises)

from ggplot import *
from ggplot.geoms.geom import geom
from ggplot.stats.stat import stat
from ggplot.utils.exceptions import GgplotError
from . import cleanup


@cleanup
def test_stat_basics():
    class stat_abc(stat):
        DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity'}
        CREATES = {'fill'}

    class stat_efg(stat):
        DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity'}
        REQUIRED_AES = {'weight'}
        CREATES = {'fill'}

    gg = ggplot(aes(x='wt', y='mpg'), mtcars)

    # stat_abc has no _calculate method
    with assert_raises(NotImplementedError):
        print(gg + stat_abc())

    # stat_efg requires 'weight' aesthetic
    with assert_raises(GgplotError):
        print(gg + stat_efg())


def test_stat_parameter_sharing():
    # When the stat has a parameter with the same name as
    # the geom aesthetic,they both get their value

    # NOTE: This test may need to be modified when the
    # geom & stat internals change
    class stat_abc(stat):
        DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity',
                          'weight': 1}
        REQUIRED_AES = {'x'}
        CREATES = {'y'}

        @classmethod
        def compute_panel(cls, data, scales, **params):
            return data

    class geom_abc(geom):
        DEFAULT_PARAMS = {'stat': 'abc', 'position': 'identity'}
        REQUIRED_AES = {'x', 'weight'}

        @staticmethod
        def draw(pinfo, scales, coordinates, ax, **kwargs):
            pass

    # TODO: Should allow for checking the environment
    # instead of monkey patching
    import ggplot as _ggplot
    _ggplot.stats.stat_abc = stat_abc

    # weight is manually set, it should be a stat parameter and
    # not a geom manual setting
    g = geom_abc(weight=4)
    assert('weight' in g.aes_params)
    assert('weight' in g._stat.params)

    g = geom_abc(aes(weight='mpg'))
    assert('weight' in g.mapping)
    assert('weight' in g._stat.params)
