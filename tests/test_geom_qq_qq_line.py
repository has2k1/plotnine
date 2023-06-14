import numpy as np
import pandas as pd

from plotnine import aes, geom_qq, geom_qq_line, ggplot

random_state = np.random.RandomState(1234567890)
normal_data = pd.DataFrame({"x": random_state.normal(size=100)})


def test_normal():
    p = ggplot(normal_data, aes(sample="x")) + geom_qq()
    # Roughly a straight line of points through the origin
    assert p == "normal"


def test_normal_with_line():
    p = ggplot(normal_data, aes(sample="x")) + geom_qq() + geom_qq_line()
    # Roughly a straight line of points through the origin
    assert p == "normal_with_line"
