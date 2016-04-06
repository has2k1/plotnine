from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_raises
import pandas as pd

from ggplot import *
from ggplot.data import *
from ggplot.geoms.geom import geom
from ggplot.utils.exceptions import GgplotError

df = pd.DataFrame({'col1': [1, 2, 3, 4],
                   'col2': 2,
                   'col3': list('abcd')})


def test_geom_basics():
    class geom_abc(geom):
        DEFAULT_AES = {'color': None}
        DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    g = geom_abc(data=df)
    assert g.data is df

    g = geom_abc(df)
    assert g.data is df

    # geom data should not mess with the main data
    df_copy = df.copy()
    p = ggplot(df, aes('col', 'mpg')) + geom_abc(df_copy)
    assert p.data is df
    assert p.layers[0].geom.data is df_copy

    g = geom_abc(aes(color='col1'))
    assert g.mapping['color'] == 'col1'

    g = geom_abc(mapping=aes(color='col2'))
    assert g.mapping['color'] == 'col2'

    # Multiple mappings
    with assert_raises(GgplotError):
        g = geom_abc(aes(color='col1'), aes(color='co1'))

    # setting, not mapping
    g = geom_abc(color='blue')
    assert g.aes_params['color'] == 'blue'


def test_geom_with_invalid_argument():
    class geom_abc(geom):
        DEFAULT_AES = {'color': None}
        DEFAULT_PARAMS = {'stat': 'identity',
                          'position': 'identity'}

    with assert_raises(GgplotError):
        geom_abc(do_the_impossible=True)
