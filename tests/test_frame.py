import narwhals as nw
import numpy as np
import pandas as pd
import polars as pl
import pytest

from plotnine._utils import frame as F

BACKENDS = [F.Implementation.PANDAS, F.Implementation.POLARS]


@pytest.fixture(params=BACKENDS, ids=["pandas", "polars"])
def impl(request):
    return request.param


def test_to_frame_native():
    df = F.to_frame(pl.DataFrame({"x": [1, 2]}))
    assert isinstance(df, nw.DataFrame)
    assert df.implementation == F.Implementation.POLARS

    pdf = pd.DataFrame({"x": [1, 2]}, index=[5, 5])
    df = F.to_frame(pdf)
    assert df.implementation == F.Implementation.PANDAS
    assert list(df.to_native().index) == [0, 1]


def test_to_frame_groupby():
    pdf = pd.DataFrame({"x": [1, 2], "g": ["a", "b"]})
    df = F.to_frame(pdf.groupby("g"))
    assert df.columns == ["x", "g"]


def test_to_frame_bad():
    with pytest.raises(TypeError):
        F.to_frame([1, 2, 3])


def test_series(impl):
    s = F.series(np.array([1.0, 2.0]), "x", backend=impl)
    assert s.dtype == nw.Float64
    assert s.name == "x"

    s = F.series(["a", None, float("nan")], "x", backend=impl)
    assert s.dtype == nw.String
    assert s.null_count() == 2

    s = F.series([(1, 2), "solid"], "x", backend=impl)
    assert s.dtype == nw.Object
    assert s.to_list() == [(1, 2), "solid"]

    s = F.series(np.array([(0, (1, 1)), "solid"], dtype=object), backend=impl)
    assert s.to_list() == [(0, (1, 1)), "solid"]

    s = F.series(
        pd.Categorical(["b", "a"], categories=["b", "a"]), backend=impl
    )
    assert F.is_categorical(s)

    d = np.array(["2020-01-01", "2021-01-01"], dtype="datetime64[D]")
    s = F.series(d, backend=impl)
    assert s.dtype == nw.Datetime or s.dtype == nw.Date


def test_frame(impl):
    df = F.frame({"x": [1, 2, 3], "y": 1, "z": "a"}, backend=impl)
    assert df.shape == (3, 3)
    assert df["y"].to_list() == [1, 1, 1]

    df = F.frame({"x": 1}, backend=impl)
    assert df.shape == (1, 1)

    df = F.frame(backend=impl)
    assert df.shape == (0, 0)

    df = F.frame({"x": [1, 2], "o": [(1, 2), (3, 4)]}, backend=impl)
    assert df["o"].to_list() == [(1, 2), (3, 4)]

    with pytest.raises(ValueError):
        F.frame({"x": [1, 2], "y": [1, 2, 3]}, backend=impl)


def test_assign(impl):
    df = F.frame({"x": [1, 2, 3]}, backend=impl)
    df = F.assign(
        df,
        a=1.5,
        b=np.array([4, 5, 6]),
        c=nw.col("x") * 2,
        d=["p", "q", "r"],
    )
    assert df.columns == ["x", "a", "b", "c", "d"]
    assert df["c"].to_list() == [2, 4, 6]
    assert df["a"].to_list() == [1.5] * 3

    df = F.assign(F.frame(backend=impl), x=[1, 2])
    assert df.shape == (2, 1)


def test_concat(impl):
    a = F.frame({"x": [1, 2], "g": ["a", "b"]}, backend=impl)
    b = F.frame({"x": [1.5], "y": [10]}, backend=impl)
    df = F.concat([a, b])
    assert df.columns == ["x", "g", "y"]
    assert df["x"].to_list() == [1, 2, 1.5]
    assert F.is_missing(df["y"]).to_list() == [True, True, False]

    # Empty frames without columns are dropped
    df = F.concat([F.frame(backend=impl), a])
    assert df.shape == (2, 2)

    # Different enums
    e1 = a.with_columns(nw.col("g").cast(nw.Enum(["a", "b"])))
    e2 = F.frame({"x": [3], "g": ["c"]}, backend=impl)
    df = F.concat([e1, e2])
    assert df["g"].to_list() == ["a", "b", "c"]


def test_group_split_order(impl):
    df = F.frame({"g": [3, 1, 2, 1], "v": [0, 1, 2, 3]}, backend=impl)
    keys = [k for k, _ in F.group_split(df, "g")]
    assert keys == [(1,), (2,), (3,)]

    # Enum order is respected
    df = df.with_columns(
        h=F.series(["b", "a", "c", "a"], backend=impl).cast(
            nw.Enum(["c", "b", "a"])
        )
    )
    keys = [k for k, _ in F.group_split(df, "h")]
    assert keys == [("c",), ("b",), ("a",)]

    # Rows keep their order within a group
    groups = dict(F.group_split(df, "g"))
    assert groups[(1,)]["v"].to_list() == [1, 3]


def test_group_split_null_keys(impl):
    df = F.frame({"g": [1, None, 1], "v": [0, 1, 2]}, backend=impl)
    keys = [k for k, _ in F.group_split(df, "g")]
    assert keys == [(1,)]


def test_group_apply(impl):
    df = F.frame({"g": [2, 1, 2], "v": [1.0, 2.0, 3.0]}, backend=impl)

    def fn(gdf):
        return F.frame(
            {"g": gdf["g"].item(0), "s": gdf["v"].sum()}, backend=impl
        )

    res = F.group_apply(df, "g", fn)
    assert res["g"].to_list() == [1, 2]
    assert res["s"].to_list() == [2.0, 4.0]


def test_is_missing(impl):
    s = F.series([1.0, None, float("nan")], backend=impl)
    assert F.is_missing(s).to_list() == [False, True, True]
    assert F.is_finite(
        F.series([1.0, np.inf, None], backend=impl)
    ).to_list() == [
        True,
        False,
        False,
    ]
    s = F.series(["a", None], backend=impl)
    assert F.is_missing(s).to_list() == [False, True]


def test_filter_take(impl):
    df = F.frame({"x": [1, 2, 3]}, backend=impl)
    assert F.filter_rows(df, np.array([True, False, True]))["x"].to_list() == [
        1,
        3,
    ]
    assert F.take(df, [2, 2, 0])["x"].to_list() == [3, 3, 1]
    assert len(F.take(df, [])) == 0


def test_levels_and_kinds():
    pdf = pd.DataFrame(
        {
            "o": pd.Categorical(
                ["b", "a"], categories=["b", "a"], ordered=True
            ),
            "u": pd.Categorical(["b", "a"], categories=["b", "a"]),
            "s": ["b", "a"],
        }
    )
    df = F.to_frame(pdf)
    assert F.levels(df["o"]) == ["b", "a"]
    assert F.levels(df["u"]) == ["b", "a"]
    assert F.levels(df["s"]) == ["a", "b"]
    assert F.is_ordinal(df["o"])
    assert not F.is_ordinal(df["u"])
    assert F.is_categorical(df["u"])
    assert not F.is_categorical(df["s"])

    pldf = F.to_frame(
        pl.DataFrame(
            {
                "e": pl.Series(["b", "a"], dtype=pl.Enum(["b", "a"])),
                "c": pl.Series(["b", "a"], dtype=pl.Categorical),
            }
        )
    )
    assert F.levels(pldf["e"]) == ["b", "a"]
    assert F.levels(pldf["c"]) == ["a", "b"]
    assert F.is_ordinal(pldf["e"])
    assert not F.is_ordinal(pldf["c"])


def test_categorical_nominal_enum():
    with F.nominal_enums_scope():
        s = F.categorical(
            [3, 1, None], [3, 1, 2], backend=F.Implementation.POLARS
        )
        assert s.dtype == nw.Enum(["3", "1", "2"])
        assert s.to_list() == ["3", "1", None]
        assert F.is_categorical(s)
        assert not F.is_ordinal(s)

        o = F.categorical(
            ["b", "a"],
            ["b", "a"],
            ordered=True,
            backend=F.Implementation.POLARS,
        )
        assert F.is_ordinal(o)

    # The record does not leak out of the scope
    with F.nominal_enums_scope():
        assert F.is_ordinal(s)


def test_categorical_pandas():
    s = F.categorical([3, 1, None], [3, 1, 2], backend=F.Implementation.PANDAS)
    cat = s.to_native()
    assert list(cat.cat.categories) == [3, 1, 2]
    assert not cat.cat.ordered
    assert not F.is_ordinal(s)
    assert F.levels(s) == [3, 1, 2]

    s = F.categorical(
        ["b", "a"], ordered=True, backend=F.Implementation.PANDAS
    )
    assert F.is_ordinal(s)
    assert F.levels(s) == ["a", "b"]


def test_sort_is_stable(impl):
    rng = np.random.default_rng(123)
    k = rng.integers(0, 3, 100_000)
    v = np.arange(len(k))
    df = F.sort(F.frame({"k": k, "v": v}, backend=impl), "k")
    for i in range(3):
        values = df.filter(nw.col("k") == i)["v"].to_numpy()
        assert np.all(np.diff(values) > 0)

    df = F.sort(F.frame({"k": k, "v": v}, backend=impl), "k", descending=True)
    assert df["k"].to_list()[0] == 2
    values = df.filter(nw.col("k") == 2)["v"].to_numpy()
    assert np.all(np.diff(values) > 0)


def test_group_split_unsorted(impl):
    df = F.frame({"g": [3, 1, 3, 2], "v": [0, 1, 2, 3]}, backend=impl)
    keys = [k for k, _ in F.group_split(df, "g", sort=False)]
    assert keys == [(3,), (1,), (2,)]
    indices = F.group_indices(df, "g", sort=False)
    assert [i.tolist() for i in indices] == [[0, 2], [1], [3]]


def test_unique_rows_object(impl):
    df = F.frame(
        {"a": [1, 1, 2], "b": [(0, (1, 1)), (0, (1, 1)), "solid"]},
        backend=impl,
    )
    assert len(F.unique_rows(df)) == 2
