import numpy as np
import pandas as pd

from plotnine.coords.coord_polar import coord_polar


def test_coord_polar_transforms_segment_endpoints_theta_x():
    coord = coord_polar(theta="x")
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [0], "y": [1], "xend": [10], "yend": [2]})

    out = coord.transform(data, None)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2


def test_coord_polar_transforms_segment_endpoints_theta_y():
    coord = coord_polar(theta="y")
    coord.params = {"theta_range": (0, 10), "r_range": (0, 10)}
    data = pd.DataFrame({"x": [1], "y": [0], "xend": [2], "yend": [10]})

    out = coord.transform(data, None)

    assert out.loc[0, "x"] == 0
    assert out.loc[0, "y"] == 1
    assert np.isclose(out.loc[0, "xend"], 2 * np.pi)
    assert out.loc[0, "yend"] == 2
