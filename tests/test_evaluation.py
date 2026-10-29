import narwhals as nw
import numpy as np
import pandas as pd
import polars as pl
import pytest

from plotnine._utils import frame as F
from plotnine.exceptions import PlotnineError
from plotnine.mapping import Environment
from plotnine.mapping.evaluation import evaluate

BACKENDS = [F.Implementation.PANDAS, F.Implementation.POLARS]


@pytest.fixture(params=BACKENDS, ids=["pandas", "polars"])
def data(request):
    return F.frame(
        {
            "x": [1.0, 2.0, 3.0, 4.0],
            "g": ["b", "a", "b", "c"],
        },
        backend=request.param,
    )


def ev(aesthetics, data):
    env = Environment.capture(1)
    return evaluate(aesthetics, data, env)


def test_column_name(data):
    res = ev({"y": "x"}, data)
    assert res["y"].to_list() == [1, 2, 3, 4]


def test_narwhals_expression(data):
    res = ev({"y": nw.col("x") * 2, "z": nw.col("x").mean()}, data)
    assert res["y"].to_list() == [2, 4, 6, 8]
    # Aggregations are broadcast
    assert res["z"].to_list() == [2.5] * 4


def test_string_expression_is_symbolic(data):
    multiplier = 10  # noqa: F841
    res = ev({"y": "np.log(x) + x * multiplier", "z": "x - x.mean()"}, data)
    assert np.allclose(
        res["y"].to_numpy(), np.log([1, 2, 3, 4]) + np.array([1, 2, 3, 4]) * 10
    )
    assert res["z"].to_list() == [-1.5, -0.5, 0.5, 1.5]
    # The result is in the same library as the data
    assert res.implementation == data.implementation


def test_string_expression_native_fallback(data):
    # np.sum does not work with narwhals expressions, it is evaluated
    # with the native series
    res = ev({"y": "x / np.sum(x)"}, data)
    assert res["y"].to_list() == [0.1, 0.2, 0.3, 0.4]

    # str() of an expression must not be mistaken for a value
    res = ev({"y": "len(x)"}, data)
    assert res["y"].to_list() == [4] * 4


def test_native_api():
    pdf = F.to_frame(pd.DataFrame({"s": ["a", "b"]}))
    res = ev({"y": "s.str.upper()"}, pdf)
    assert res["y"].to_list() == ["A", "B"]

    pldf = F.to_frame(pl.DataFrame({"s": ["a", "b"]}))
    res = ev({"y": "s.str.to_uppercase()"}, pldf)
    assert res["y"].to_list() == ["A", "B"]


def test_constants_and_values(data):
    res = ev({"y": "'red'", "z": [4, 3, 2, 1], "w": 5}, data)
    assert res["y"].to_list() == ["red"] * 4
    assert res["z"].to_list() == [4, 3, 2, 1]
    assert res["w"].to_list() == [5] * 4


def test_no_data():
    empty = F.frame(backend=F.Implementation.POLARS)
    res = ev({"x": [1, 2, 3], "y": 2}, empty)
    assert res.shape == (3, 2)
    res = ev({"y": 2}, empty)
    assert res.shape == (1, 1)


def test_bad_expression(data):
    with pytest.raises(PlotnineError, match="Could not evaluate"):
        ev({"y": "undefined_variable + x"}, data)

    with pytest.raises(PlotnineError, match="same length"):
        ev({"y": [1, 2]}, data)


def test_factor(data):
    with F.nominal_enums_scope():
        res = ev({"c": "factor(g)"}, data)
        assert F.is_categorical(res["c"])
        assert F.levels(res["c"]) == ["a", "b", "c"]
        assert not F.is_ordinal(res["c"])

    with F.nominal_enums_scope():
        res = ev({"o": "factor(g, ordered=True)"}, data)
        assert F.is_ordinal(res["o"])

        res = ev({"c": "factor(x, categories=[4.0, 3.0, 2.0, 1.0])"}, data)
        assert [str(v) for v in F.levels(res["c"])] == [
            "4.0",
            "3.0",
            "2.0",
            "1.0",
        ]
        assert not F.is_ordinal(res["c"])


def test_reorder(data):
    res = ev({"c": "reorder(g, x)"}, data)
    # a=2, b=(1+3)/2=2, c=4; ties are broken by the category order
    assert F.levels(res["c"]) == ["a", "b", "c"]
    res = ev({"c": "reorder(g, -x)"}, data)
    assert F.levels(res["c"]) == ["c", "a", "b"]
