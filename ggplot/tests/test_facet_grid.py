from __future__ import absolute_import, division, print_function

from nose.tools import assert_equal, assert_is, assert_is_not
from nose.tools import assert_raises
import pandas as pd
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


def test_facet_grid_labelling():
    sub_01 = {'0': 'zero', '1': 'one'}
    sub_345 = {'3': 'three', '4': 'four', '5': 'five'}

    def blahblah_string(label_info):
        return 'blahblah'

    to_string = as_labeller(sub_01)

    # 1. Along the columns
    label_info = pd.Series([3], index=['gear'])
    label_info._meta = {'dimension': 'cols'}

    # label_both
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_both))
    labels = f.labeller(label_info)
    assert_equal(labels[0], 'gear: 3')

    # lookup table
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_both, gear=sub_345))
    labels = f.labeller(label_info)
    assert_equal(labels[0], 'three')

    # 2. Along the rows
    label_info = pd.Series([1, 0], index=['vs', 'am'])
    label_info._meta = {'dimension': 'rows'}

    # label_value
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_value,
                                     multi_line=False))
    labels = f.labeller(label_info)
    assert_equal(labels[0], '1, 0')

    # label_value, multi_line
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_value,
                                     multi_line=True))
    labels = f.labeller(label_info)
    assert_equal(list(labels), ['1', '0'])

    # label_both
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_both,
                                     multi_line=False))
    labels = f.labeller(label_info)
    assert_equal(labels[0], 'vs: 1, am: 0')

    # label_both, lookup table
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_both,
                                     multi_line=False,
                                     am=sub_01))
    labels = f.labeller(label_info)
    assert_equal(labels[0], 'vs: 1, zero')

    # label_both, as_labeller with function
    f = facet_grid('vs + am ~ gear',
                   labeller=labeller(default=label_both,
                                     multi_line=False,
                                     vs=blahblah_string))
    labels = f.labeller(label_info)
    assert_equal(labels[0], 'blahblah, am: 0')

    # as_labeller
    f = facet_grid('vs + am ~ gear', labeller=to_string)
    labels = f.labeller(label_info)
    assert_equal(list(labels), ['one', 'zero'])
