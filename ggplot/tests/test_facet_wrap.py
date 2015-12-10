from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal, assert_is, assert_is_not, assert_raises
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
