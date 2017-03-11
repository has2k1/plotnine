from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import random
import string
import itertools
import warnings

import numpy as np
import pandas as pd

from plotnine.data import mtcars
from plotnine.utils import _margins, add_margins, ninteraction
from plotnine.utils import join_keys, match, uniquecols, defaults
from plotnine.utils import remove_missing, groupby_with_null


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
    df = mtcars.loc[:, ['mpg', 'disp', 'vs', 'am', 'gear']]
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
        assert rank == rank_df

    # duplicates are numbered sequentially
    # df                    ids
    # [6, 6, 4, 4, 5, 5] -> [3, 3, 1, 1, 2, 2]
    for case in simple_vectors:
        rank = pd.DataFrame(case).rank(method='min')
        rank = rank[0].astype(int).repeat(2).tolist()
        rank_df = ninteraction(
            pd.DataFrame(np.array(case).repeat(2)))
        assert rank == rank_df

    # grids are correctly ranked
    df = pd.DataFrame(list(itertools.product([1, 2], range(1, 11))))
    assert ninteraction(df) == list(range(1, len(df)+1))
    assert ninteraction(df, drop=True) == list(range(1, len(df)+1))

    # zero length dataframe
    df = pd.DataFrame()
    assert ninteraction(df) == []


def test_join_keys():
    df1 = pd.DataFrame({'a': [0, 0, 1, 1, 2, 2],
                        'b': [0, 1, 2, 3, 1, 2],
                        'c': [0, 1, 2, 3, 4, 5]})

    # same array and columns the keys should be the same
    keys = join_keys(df1, df1, ['a', 'b'])
    assert list(keys['x']) == [1, 2, 3, 4, 5, 6]
    assert list(keys['x']) == [1, 2, 3, 4, 5, 6]

    # Every other element of df2['b'] is changed
    # so every other key should be different
    df2 = pd.DataFrame({'a': [0, 0, 1, 1, 2, 2],
                        'b': [0, 11, 2, 33, 1, 22],
                        'c': [1, 2, 3, 4, 5, 6]})

    keys = join_keys(df1, df2, ['a', 'b'])
    assert list(keys['x']) == [1, 2, 4, 5, 7, 8]
    assert list(keys['y']) == [1, 3, 4, 6, 7, 9]


def test_match():
    v1 = [1, 1, 2, 2, 3, 3]
    v2 = [1, 2, 3]
    v3 = [0, 1, 2]
    c = [1]

    assert match(v1, v2) == [0, 0, 1, 1, 2, 2]
    assert match(v1, v2, incomparables=c) == [-1, -1, 1, 1, 2, 2]
    assert match(v1, v3) == [1, 1, 2, 2, -1, -1]


def test_uniquecols():
    df = pd.DataFrame({'x': [1, 2, 3, 4],
                       'y': ['a', 'b', 'c', 'd'],
                       'z': [8] * 4,
                       'other': ['same']*4})
    df2 = pd.DataFrame({'z': [8],
                        'other': ['same']})
    result = uniquecols(df)
    assert result.equals(df2)


def test_defaults():
    d1 = {'a': 1, 'b': 2, 'c': 3}
    d2 = {'a': 11, 'd': 4}
    d3 = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

    defaults(d1, d2)
    assert d1 == d3


def test_remove_missing():
    df = pd.DataFrame({'a': [1.0, np.NaN, 3, np.inf],
                       'b': [1, 2, 3, 4]})
    df2 = pd.DataFrame({'a': [1.0, 3, np.inf],
                       'b': [1, 3, 4]})
    df3 = pd.DataFrame({'a': [1.0, 3],
                       'b': [1, 3]})

    with warnings.catch_warnings(record=True) as w:
        res = remove_missing(df, na_rm=True, vars=['b'])
        res.equals(df)

        res = remove_missing(df)
        res.equals(df2)

        res = remove_missing(df, na_rm=True, finite=True)
        res.equals(df3)
        assert len(w) == 1


def test_groupby_with_null():
    df = pd.DataFrame({'x': [1, 2, 3, 4, 5, 6],
                       'y': ['a', 'a', None, None, 'b', 'b'],
                       'z': [1, 1, np.NaN, np.NaN, 3, 3]})

    assert(len(list(groupby_with_null(df, 'x'))) == 6)
    assert(len(list(groupby_with_null(df, 'y'))) == 3)
    assert(len(list(groupby_with_null(df, 'z'))) == 3)
