import pandas as pd
import pytest

from plotnine import (
    aes,
    dup_axis,
    geom_point,
    ggplot,
    scale_x_continuous,
    scale_x_datetime,
    sec_axis,
)
from plotnine.exceptions import PlotnineError


def test_non_monotonic_transform():
    df = pd.DataFrame({"x": [-5.0, 5.0], "y": [0.0, 1.0]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + scale_x_continuous(sec_axis=sec_axis(lambda x: x**2))
    )
    with pytest.raises(PlotnineError, match="monotonic"):
        p.build_test()


def test_labels_copy_requires_breaks_copy():
    with pytest.raises(PlotnineError):
        sec_axis(lambda x: x + 1, labels=None)


def test_datetime_rejects_sec_axis():
    with pytest.raises(PlotnineError):
        scale_x_datetime(sec_axis=dup_axis())
