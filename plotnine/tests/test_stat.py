import pytest
import numpy as np

from plotnine import ggplot, aes, geom_bar
from plotnine.data import mtcars
from plotnine.geoms.geom import geom
from plotnine.stats.stat import stat
from plotnine.exceptions import PlotnineError, PlotnineWarning


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
    with pytest.raises(NotImplementedError):
        print(gg + stat_abc())

    # stat_efg requires 'weight' aesthetic
    with pytest.raises(PlotnineError):
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
        DEFAULT_PARAMS = {'stat': stat_abc, 'position': 'identity'}
        REQUIRED_AES = {'x', 'weight'}

        @staticmethod
        def draw(pinfo, panel_params, coord, ax, **kwargs):
            pass

    # weight is manually set, it should be a stat parameter and
    # not a geom manual setting
    g = geom_abc(weight=4)
    assert('weight' in g.aes_params)
    assert('weight' in g._stat.params)

    g = geom_abc(aes(weight='mpg'))
    assert('weight' in g.mapping)
    assert('weight' in g._stat.params)


def test_calculated_expressions():
    p = (ggplot(mtcars, aes(x='factor(cyl)', y='..count..+1'))
         + geom_bar())
    # No exception
    p._build()


def test_removes_infinite_values():
    df = mtcars.copy()
    df.loc[[0, 5], 'wt'] = [np.inf, -np.inf]
    p = ggplot(df, aes(x='wt')) + geom_bar()

    with pytest.warns(PlotnineWarning) as record:
        p._build()

    def removed_2_row_with_infinites(record):
        for item in record:
            msg = str(item.message).lower()
            if '2 rows' in msg and 'non-finite' in msg:
                return True
        return False

    assert removed_2_row_with_infinites(record)
