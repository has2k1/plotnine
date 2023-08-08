import os

import numpy as np
import pandas as pd
import pytest

from plotnine import aes, annotate, geom_point, ggplot, scale_y_symlog

is_CI = os.environ.get("CI") is not None


@pytest.mark.skipif(is_CI, reason="mizani not yet shipped")
def test_scale_y_symlog():
    n = 3
    x = np.arange(-n, n + 1)
    data = pd.DataFrame({"x": x, "y": np.sign(x) * (10 ** np.abs(x))})

    p = (
        ggplot(data, aes("x", "y"))
        + geom_point()
        # Minor grid lines
        + annotate(
            "point",
            x=0,
            y=[-550, -55, -5, 5, 55, 550],
            color="red",
            shape="_",
            size=12,
        )
        + scale_y_symlog()
    )
    assert p == "scale_y_symlog"
