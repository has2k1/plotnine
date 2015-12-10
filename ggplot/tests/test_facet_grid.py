from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal, assert_is, assert_is_not, assert_raises
from ggplot import *
from ggplot.utils.exceptions import GgplotError
from ggplot.facets.facet_grid import parse_grid_facets


def test_facet_grid_formula():
    parse = parse_grid_facets

    assert_equal(parse('var1 ~ .'), (['var1'], []))
    assert_equal(parse('. ~ var2'), ([], ['var2']))
    assert_equal(parse('var1 ~ var2'), (['var1'], ['var2']))
    assert_equal(parse('var1 + var2 ~ var3'), (['var1', 'var2'],
                                               ['var3']))
    assert_equal(parse('var1 + var2 ~ .'), (['var1', 'var2'], []))
    assert_equal(parse('var1 + var2 ~ var3 + var4'), (['var1', 'var2'],
                                                      ['var3', 'var4']))
    assert_equal(parse('var1+var2~var3+var4'), (['var1', 'var2'],
                                                ['var3', 'var4']))
    assert_raises(GgplotError, parse, 'var1')
    assert_raises(GgplotError, parse, 'var1 + var2')
