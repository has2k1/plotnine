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
    # the geom aesthetic, if that aesthetic is manually set
    # to a scalar when the geom is creates, then the stat
    # takes it as a parameter. If that aesthetic is mapped,
    # then the geom takes it as a mapping

    # NOTE: This test may need to be modified when the
    # layer class is created and the geom & stat internals
    # change
    class stat_abc(stat):
        DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity',
                          'weight': 1}
        REQUIRED_AES = {'x'}
        CREATES = {'y'}
        def _calculate(self, data):
            return data

    class geom_abc(geom):
        DEFAULT_PARAMS = {'stat': 'stat_abc', 'position': 'identity'}
        REQUIRED_AES = {'x', 'weight'}
        def _plot_unit(self, pinfo, ax):
            pass
        def _get_stat_type(self, kwargs):
            return stat_abc

    # weight is manually set, it should be a stat parameter and
    # not a geom manual setting
    _geom = geom_abc(weight=4)
    with assert_raises(KeyError):
        w = _geom.aes['weight']
    with assert_raises(KeyError):
        w = _geom.manual_aes['weight']
    assert_equal(_geom._stat_params['weight'], 4)

    # weight is mapped set, it should be a geom aesthetic
    # and the stat parameter should still have the default value
    _geom = geom_abc(aes(weight='mpg'))
    w = _geom.aes['weight']  # No keyError
    with assert_raises(KeyError):
        w = _geom.manual_aes['weight']
    with assert_raises(KeyError):
        w = _geom._stat_params['weight']
