from __future__ import absolute_import, division, print_function

from nose.tools import assert_equal, assert_is, assert_is_not
from nose.tools import assert_raises
import pandas as pd
from ggplot import *
from ggplot.utils.exceptions import GgplotError
from ggplot.facets.facet_wrap import parse_wrap_facets


def test_facet_wrap_formula():
    parse = parse_wrap_facets
    assert_equal(parse('~var1'), ['var1'])
    assert_equal(parse('~var1 + var2'), ['var1', 'var2'])
    assert_equal(parse(['var1', 'var2']), ['var1', 'var2'])
    assert_raises(GgplotError, parse, 'var1')
    assert_raises(GgplotError, parse, 'var1 + var2')


def test_facet_grid_labelling():
    def appender(string, suffix="-foo"):
        return string + suffix

    label_info = pd.Series([0], index=['am'])

    # Turn string function into labeller function
    f = facet_wrap('~am', labeller=as_labeller(appender))
    labels = f.labeller(label_info)
    assert_equal(labels[0], '0-foo')
