import numpy as np
import pandas as pd

from plotnine import aes, ggplot, stat_summary_bin

data = pd.DataFrame(
    {
        "xd": list("aaaaabbbbcccccc"),
        "xc": range(15),
        "y": [1, 2, 3, 4, 5, 1.5, 1.5, 6, 6, 5, 5, 5, 5, 5, 5],
    }
)


def test_discrete_x():
    p = ggplot(data, aes("xd", "y")) + stat_summary_bin(
        fun_y=np.mean, fun_ymin=np.min, fun_ymax=np.max, geom="bar"
    )

    assert p == "discrete_x"


def test_continuous_x():
    p = ggplot(data, aes("xc", "y")) + stat_summary_bin(
        fun_y=np.mean, fun_ymin=np.min, fun_ymax=np.max, bins=5, geom="bar"
    )

    assert p == "continuous_x"


def test_setting_binwidth():
    p = ggplot(data, aes("xc", "y")) + stat_summary_bin(binwidth=3, geom="bar")
    assert p == "setting_binwidth"
