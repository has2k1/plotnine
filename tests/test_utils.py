import itertools
import random
import string
import warnings

import numpy as np
import pandas as pd

from plotnine._utils import (
    _margins,
    add_margins,
    join_keys,
    match,
    ninteraction,
    pivot_apply,
    remove_missing,
    uniquecols,
)
from plotnine.data import mtcars


def test__margins():
    vars = [("vs", "am"), ("gear",)]
    lst = _margins(vars, True)
    assert lst == [
        [],
        ["vs", "am"],
        ["am"],
        ["gear"],
        ["vs", "am", "gear"],
        ["am", "gear"],
    ]

    lst = _margins(vars, False)
    assert lst == []

    lst = _margins(vars, ["vs"])
    assert lst == [[], ["vs", "am"]]

    lst = _margins(vars, ["am"])
    assert lst == [[], ["am"]]

    lst = _margins(vars, ["vs", "am"])
    assert lst == [[], ["vs", "am"], ["am"]]

    lst = _margins(vars, ["gear"])
    assert lst == [[], ["gear"]]


def test_add_margins():
    data = mtcars.loc[:, ["mpg", "disp", "vs", "am", "gear"]]
    n = len(data)
    all_lst = ["(all)"] * n

    vars = [("vs", "am"), ("gear",)]
    datax = add_margins(data, vars, True)

    assert datax["vs"].dtype == "category"
    assert datax["am"].dtype == "category"
    assert datax["gear"].dtype == "category"

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

    assert all(datax.loc[0 : n - 1, "am"] != all_lst)
    assert all(datax.loc[0 : n - 1, "vs"] != all_lst)
    assert all(datax.loc[0 : n - 1, "gear"] != all_lst)

    assert all(datax.loc[n : 2 * n - 1, "vs"] == all_lst)
    assert all(datax.loc[n : 2 * n - 1, "am"] == all_lst)

    assert all(datax.loc[2 * n : 3 * n - 1, "am"] == all_lst)

    assert all(datax.loc[3 * n : 4 * n - 1, "gear"] == all_lst)

    assert all(datax.loc[4 * n : 5 * n - 1, "am"] == all_lst)
    assert all(datax.loc[4 * n : 5 * n - 1, "vs"] == all_lst)
    assert all(datax.loc[4 * n : 5 * n - 1, "gear"] == all_lst)

    assert all(datax.loc[5 * n : 6 * n - 1, "am"] == all_lst)
    assert all(datax.loc[5 * n : 6 * n - 1, "gear"] == all_lst)


def test_ninteraction():
    simple_vectors = [
        list(string.ascii_lowercase),
        random.sample(string.ascii_lowercase, 26),
        list(range(1, 27)),
    ]

    # vector of unique values is equivalent to rank
    for case in simple_vectors:
        data = pd.DataFrame(case)
        rank = data.rank(method="min")
        rank = rank[0].astype(int).tolist()
        rank_data = ninteraction(data)
        assert rank == rank_data

    # duplicates are numbered sequentially
    # data                    ids
    # [6, 6, 4, 4, 5, 5] -> [3, 3, 1, 1, 2, 2]
    for case in simple_vectors:
        rank = pd.DataFrame(case).rank(method="min")
        rank = rank[0].astype(int).repeat(2).tolist()
        rank_data = ninteraction(pd.DataFrame(np.array(case).repeat(2)))
        assert rank == rank_data

    # grids are correctly ranked
    data = pd.DataFrame(list(itertools.product([1, 2], range(1, 11))))
    assert ninteraction(data) == list(range(1, len(data) + 1))
    assert ninteraction(data, drop=True) == list(range(1, len(data) + 1))

    # zero length dataframe
    data = pd.DataFrame()
    assert ninteraction(data) == []

    # dataframe with single variable
    data = pd.DataFrame({"a": ["a"]})
    assert ninteraction(data) == [1]

    data = pd.DataFrame({"a": ["b"]})
    assert ninteraction(data) == [1]


def test_ninteraction_datetime_series():
    # When a pandas datetime is converted Numpy datetime, the two
    # no longer compare as equal! This test ensures that case is
    # not happening
    lst = ["2020-01-01", "2020-01-02", "2020-01-03"]
    data1 = pd.DataFrame(
        {
            "x": list("abcaabbcc"),
            "date_list": lst * 3,
        }
    )
    data2 = pd.DataFrame(
        {
            "x": list("abcaabbcc"),
            "date_list": pd.to_datetime(lst * 3),
        }
    )

    assert ninteraction(data1) == ninteraction(data2)


def test_join_keys():
    data1 = pd.DataFrame(
        {
            "a": [0, 0, 1, 1, 2, 2],
            "b": [0, 1, 2, 3, 1, 2],
            "c": [0, 1, 2, 3, 4, 5],
        }
    )

    # same array and columns the keys should be the same
    keys = join_keys(data1, data1, ["a", "b"])
    assert list(keys["x"]) == [1, 2, 3, 4, 5, 6]
    assert list(keys["x"]) == [1, 2, 3, 4, 5, 6]

    # Every other element of data2['b'] is changed
    # so every other key should be different
    data2 = pd.DataFrame(
        {
            "a": [0, 0, 1, 1, 2, 2],
            "b": [0, 11, 2, 33, 1, 22],
            "c": [1, 2, 3, 4, 5, 6],
        }
    )

    keys = join_keys(data1, data2, ["a", "b"])
    assert list(keys["x"]) == [1, 2, 4, 5, 7, 8]
    assert list(keys["y"]) == [1, 3, 4, 6, 7, 9]


def test_match():
    v1 = [1, 1, 2, 2, 3, 3]
    v2 = [1, 2, 3]
    v3 = [0, 1, 2]
    c = [1]

    assert list(match(v1, v2)) == [0, 0, 1, 1, 2, 2]
    assert list(match(v1, v2, incomparables=c)) == [-1, -1, 1, 1, 2, 2]
    assert list(match(v1, v3)) == [1, 1, 2, 2, -1, -1]


def test_uniquecols():
    data = pd.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": ["a", "b", "c", "d"],
            "z": [8] * 4,
            "other": ["same"] * 4,
        }
    )
    data2 = pd.DataFrame({"z": [8], "other": ["same"]})
    result = uniquecols(data)
    assert result.equals(data2)


def test_remove_missing():
    data = pd.DataFrame({"a": [1.0, np.nan, 3, np.inf], "b": [1, 2, 3, 4]})
    data2 = pd.DataFrame({"a": [1.0, 3, np.inf], "b": [1, 3, 4]})
    data3 = pd.DataFrame({"a": [1.0, 3], "b": [1, 3]})

    with warnings.catch_warnings(record=True) as w:
        res = remove_missing(data, na_rm=True, vars=["b"])
        res.equals(data)

        res = remove_missing(data)
        res.equals(data2)

        res = remove_missing(data, na_rm=True, finite=True)
        res.equals(data3)
        assert len(w) == 1


def test_pivot_apply():
    data = pd.DataFrame(
        {
            "id": list("abcabc"),
            "x": [1, 2, 3, 11, 22, 33],
            "y": [1, 2, 3, 11, 22, 33],
        }
    )

    res1 = pivot_apply(data, "x", "id", np.min)
    res2 = pivot_apply(data, "y", "id", np.max)

    assert res1.index.tolist() == list("abc")
    assert res1.index.name == "id"
    assert (res1 + res2 == [12, 24, 36]).all()
