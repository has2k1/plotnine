"""
Plots with the data of the other dataframe libraries that narwhals
supports

The whole test suite runs with pandas and polars data. These tests
check that plots with the data of other libraries can be drawn.
"""

import pytest

from plotnine import (
    aes,
    facet_grid,
    geom_bar,
    geom_boxplot,
    geom_histogram,
    geom_point,
    geom_smooth,
    geom_violin,
    ggplot,
)
from plotnine.data import load_dataset

pa = pytest.importorskip("pyarrow")
pytest.importorskip("polars")

mpg = load_dataset("mpg", backend="polars").to_arrow()

PLOTS = {
    "points": ggplot(mpg, aes("displ", "hwy", color="factor(cyl)"))
    + geom_point(),
    "histogram": ggplot(mpg, aes("hwy")) + geom_histogram(bins=10),
    "boxplot": ggplot(mpg, aes("class", "hwy")) + geom_boxplot(),
    "smooth": ggplot(mpg, aes("displ", "hwy")) + geom_smooth(method="lm"),
    "bar": ggplot(mpg, aes("class", fill="drv")) + geom_bar(),
    "facets": ggplot(mpg, aes("displ", "hwy"))
    + geom_point()
    + facet_grid("drv", "cyl"),
    "violin": ggplot(mpg, aes("drv", "hwy")) + geom_violin(),
}


@pytest.mark.parametrize("name", PLOTS)
def test_pyarrow_table(name):
    p = PLOTS[name]
    data = p.layer_data()
    assert isinstance(data, pa.Table)
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]


def test_empty_polars_dataframe():
    # The columns of an empty polars dataframe have no type
    import polars as pl

    p = ggplot(pl.DataFrame({"x": [], "y": []}), aes("x", "y")) + geom_point()
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]


@pytest.mark.parametrize("library", ["pandas", "polars", "pyarrow"])
def test_timedelta_column(library):
    from datetime import timedelta

    import pandas as pd

    from plotnine import geom_line

    df = pd.DataFrame(
        {
            "x": [timedelta(days=i, hours=3 * i) for i in range(10)],
            "y": range(10),
        }
    )
    if library == "polars":
        import polars as pl

        df = pl.from_pandas(df)
    elif library == "pyarrow":
        df = pa.Table.from_pandas(df)

    p = ggplot(df, aes("x", "y")) + geom_line()
    p.draw_test()  # pyright: ignore[reportAttributeAccessIssue]
