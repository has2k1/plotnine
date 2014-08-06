from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import random
import string
import itertools
from nose.tools import assert_equal, assert_true, assert_raises

import numpy as np
import pandas as pd
import scipy.stats as ss

from . import get_assert_same_ggplot, cleanup
from ..exampledata import mtcars
from ..utils.utils import _margins, add_margins, ninteraction
from ..scales.utils import censor, zero_range, expand_range

assert_same_ggplot = get_assert_same_ggplot(__file__)


def test__margins():
    vars = [('vs', 'am'), ('gear',)]
    lst = _margins(vars, True)
    assert(lst == [[],
                   ['vs', 'am'],
                   ['am'],
                   ['gear'],
                   ['vs', 'am', 'gear'],
                   ['am', 'gear']])

    lst = _margins(vars, False)
    assert(lst == [])

    lst = _margins(vars, ['vs'])
    assert(lst == [[],
                   ['vs', 'am']])

    lst = _margins(vars, ['am'])
    assert(lst == [[],
                   ['am']])

    lst = _margins(vars, ['vs', 'am'])
    assert(lst == [[],
                   ['vs', 'am'],
                   ['am']])

    lst = _margins(vars, ['gear'])
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


def test_censor():
    x = range(10)
    xx = censor(x, (2, 8))
    assert(np.isnan(xx[0]))
    assert(np.isnan(xx[1]))
    assert(np.isnan(xx[9]))

    df = pd.DataFrame({'x': x, 'y': range(10)})
    df['x'] = censor(df['x'], (2, 8))
    assert(np.isnan(df['x'][0]))
    assert(np.isnan(df['x'][1]))
    assert(np.isnan(df['x'][9]))

    df['y'] = censor(df['y'], (-2, 18))
    assert(issubclass(df['y'].dtype.type, np.integer))


def test_ninteraction():
    simple_vectors = [
      list(string.ascii_lowercase),
      random.sample(string.ascii_lowercase, 26),
      list(range(1, 27))]

    # vector of unique values is equivalent to rank
    for case in simple_vectors:
        rank = pd.DataFrame(case).rank(method='min')
        rank = rank[0].astype(int).tolist()
        rank_df = ninteraction(pd.DataFrame(case))
        assert(rank == rank_df)

    # duplicates are numbered sequentially
    # df                    ids
    # [6, 6, 4, 4, 5, 5] -> [3, 3, 1, 1, 2, 2]
    for case in simple_vectors:
        rank = pd.DataFrame(case).rank(method='min')
        rank = rank[0].astype(int).repeat(2).tolist()
        rank_df = ninteraction(
            pd.DataFrame(np.array(case).repeat(2)))
        assert(rank == rank_df)

    # grids are correctly ranked
    df = pd.DataFrame(list(itertools.product([1, 2], range(1, 11))))
    assert(ninteraction(df) == list(range(1, len(df)+1)))
    assert(ninteraction(df, drop=True) == list(range(1, len(df)+1)))

    # zero length dataframe
    df = pd.DataFrame()
    assert(ninteraction(df) == [])


def test_zero_range():
    c = np.array
    eps = np.finfo(float).eps

    assert(zero_range(c((1, 1 + eps))))
    assert(zero_range(c((1, 1 + 99 * eps))))
    assert(not zero_range(c((1, 1 + 101 * eps)))) # Crossed the tol threshold
    assert(not zero_range(c((1, 1 + 2 * eps)), tol = eps)) # Changed tol

    # Scaling up or down all the values has no effect since the values
    # are rescaled to 1 before checking against tol
    assert(zero_range(100000 * c((1, 1 + eps))))
    assert(not zero_range(100000 * c((1, 1 + 200 * eps))))
    assert(zero_range(.00001 * c((1, 1 + eps))))
    assert(not zero_range(.00001 * c((1, 1 + 200 * eps))))

    # NA values
    assert(zero_range((1, np.nan)))

    # Infinite values
    assert(not zero_range((1, np.inf)))
    assert(not zero_range((-np.inf, np.inf)))
    assert(zero_range((np.inf, np.inf)))

def test_expand_range():
    assert(expand_range((0, 1)) == (0, 1))
    assert(expand_range((0, 1), mul=2) == (-2, 3))
    assert(expand_range((0, 1), add=2) == (-2, 3))
    assert(expand_range((0, 1), mul=2, add=2) == (-4, 5))
    assert(expand_range((1, 1), mul=2, add=2, zero_width=1) == (0.5, 1.5))
