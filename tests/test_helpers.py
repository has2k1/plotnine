from typing import cast

import numpy.testing as npt
import pandas as pd

from plotnine import aes, facet_wrap, geom_bar, geom_point, ggplot
from plotnine.helpers import get_aesthetic_limits


class TestGetAestheticLimits:
    data = pd.DataFrame(
        {
            "x": [0, 1, 2, 3, 4, 5, 6],
            "y": [0, 1, 2, 3, 4, 5, 6],
            "g": list("aabbbcc"),
        }
    )

    def test_continuous_limits(self):
        p = ggplot(self.data, aes("x", "y")) + geom_point()
        limits = cast("tuple[float, float]", get_aesthetic_limits(p, "x"))
        npt.assert_array_almost_equal(limits, [0, 6])

    def test_discrete_limits(self):
        p = ggplot(self.data, aes("g")) + geom_bar()
        limits = cast("list[str]", get_aesthetic_limits(p, "x"))
        assert limits == ["a", "b", "c"]

    def test_facet_limits(self):
        p = (
            ggplot(self.data, aes("x", "y"))
            + geom_point()
            + facet_wrap("g", scales="free_x")
        )
        limits = cast(
            "list[tuple[float, float]]", get_aesthetic_limits(p, "x")
        )
        npt.assert_array_almost_equal(limits[0], [0, 1])
        npt.assert_array_almost_equal(limits[1], [2, 4])
        npt.assert_array_almost_equal(limits[2], [5, 6])
