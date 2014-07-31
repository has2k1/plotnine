from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal, assert_true, assert_raises

from . import get_assert_same_ggplot, cleanup
assert_same_ggplot = get_assert_same_ggplot(__file__)

import numpy as np
import pandas as pd

from ..exampledata import mtcars
from ..utils.utils import margins, add_margins


def test_margins():
    vars = [('vs', 'am'), ('gear',)]
    lst = margins(vars, True)
    assert(lst == [[],
                   ['vs', 'am'],
                   ['am'],
                   ['gear'],
                   ['vs', 'am', 'gear'],
                   ['am', 'gear']])

    lst = margins(vars, False)
    assert(lst == [])

    lst = margins(vars, ['vs'])
    assert(lst == [[],
                   ['vs', 'am']])

    lst = margins(vars, ['am'])
    assert(lst == [[],
                   ['am']])

    lst = margins(vars, ['vs', 'am'])
    assert(lst == [[],
                   ['vs', 'am'],
                   ['am']])

    lst = margins(vars, ['gear'])
    assert(lst == [[],
                   ['gear']])

def test_add_margins():
    df = mtcars.loc[:, ['mpg','disp', 'vs', 'am', 'gear']]
    n = len(df)
    all_lst = ['(all)'] * n

    vars = [('vs', 'am'), ('gear',)]
    dfx = add_margins(df, vars, True)

    assert(dfx['vs'].dtype == 'category')
    assert(dfx['am'].dtype == 'category')
    assert(dfx['gear'].dtype == 'category')

    # What we expect, where each row is of
    # column length n
    #
    # mpg   disp   vs     am     gear
    # ---   ----   --     --     ----
    # *     *      *      *      *
    # *     *      (all)  (all)  *
    # *     *      *      (all)  *
    # *     *      *      *      (all)
    # *     *      (all)  (all)  (all)
    # *     *      *      (all)  (all)

    assert(all(dfx.loc[0:n-1, 'am'] != all_lst))
    assert(all(dfx.loc[0:n-1, 'vs'] != all_lst))
    assert(all(dfx.loc[0:n-1, 'gear'] != all_lst))

    assert(all(dfx.loc[n:2*n-1, 'vs'] == all_lst))
    assert(all(dfx.loc[n:2*n-1, 'am'] == all_lst))

    assert(all(dfx.loc[2*n:3*n-1, 'am'] == all_lst))

    assert(all(dfx.loc[3*n:4*n-1, 'gear'] == all_lst))

    assert(all(dfx.loc[4*n:5*n-1, 'am'] == all_lst))
    assert(all(dfx.loc[4*n:5*n-1, 'vs'] == all_lst))
    assert(all(dfx.loc[4*n:5*n-1, 'gear'] == all_lst))

    assert(all(dfx.loc[5*n:6*n-1, 'am'] == all_lst))
    assert(all(dfx.loc[5*n:6*n-1, 'gear'] == all_lst))
