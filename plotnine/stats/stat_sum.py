import narwhals as nw

from .._utils import frame, groupby_apply
from ..doctools import document
from ..mapping.aes import ALL_AESTHETICS
from ..mapping.evaluation import after_stat
from .stat import stat


@document
class stat_sum(stat):
    """
    Sum unique values

    Useful for overplotting on scatterplots.

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_point : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "n"     # Number of observations at a position
    "prop"  # Ratio of points in that panel at a position
    ```
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {"geom": "point"}
    DEFAULT_AES = {"size": after_stat("n"), "weight": 1}
    CREATES = {"n", "prop"}

    def compute_panel(self, data, scales):
        if "weight" not in data.columns:
            data = data.with_columns(weight=nw.lit(1))

        s: set[str] = set(data.columns) & ALL_AESTHETICS
        by = [c for c in data.columns if c in s and c != "weight"]

        # Do a weighted count
        counts = groupby_apply(
            data,
            by,
            lambda df: df.head(1).with_columns(n=nw.lit(df["weight"].sum())),
        )

        # Calculate proportion values
        counts = counts.with_columns(
            prop=nw.col("n") / nw.col("n").sum().over("group")
        )
        return frame.sort(counts, "group")
