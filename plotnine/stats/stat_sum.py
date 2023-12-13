from .._utils import groupby_apply
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
    DEFAULT_PARAMS = {"geom": "point", "position": "identity", "na_rm": False}
    DEFAULT_AES = {"size": after_stat("n"), "weight": 1}
    CREATES = {"n", "prop"}

    @classmethod
    def compute_panel(cls, data, scales, **params):
        if "weight" not in data:
            data["weight"] = 1

        def count(df):
            """
            Do a weighted count
            """
            df["n"] = df["weight"].sum()
            return df.iloc[0:1]

        def ave(df):
            """
            Calculate proportion values
            """
            df["prop"] = df["n"] / df["n"].sum()
            return df

        # group by all present aesthetics other than the weight,
        # then sum them (i.e no. of uniques) to get the raw count
        # 'n', and the proportions 'prop' per group
        s: set[str] = set(data.columns) & ALL_AESTHETICS
        by = list(s.difference(["weight"]))
        counts = groupby_apply(data, by, count)
        counts = groupby_apply(counts, "group", ave)
        return counts
