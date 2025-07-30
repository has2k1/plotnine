import numpy as np
import pandas as pd

from plotnine import aes, geom_point, geom_quantile, ggplot

n = 200  # Should not be too big, affects the test duration
random_state = np.random.RandomState(1234567890)
# points that diverge like a point flash-light
data = pd.DataFrame(
    {"x": np.arange(n), "y": np.arange(n) * (1 + random_state.rand(n))}
)


def test_lines():
    p = (
        ggplot(data, aes(x="x", y="y"))
        + geom_point(alpha=0.5)
        + geom_quantile(quantiles=[0.001, 0.5, 0.999], formula="y~x", size=2)
    )

    # np.absolute tests the ability to pickup variables in the
    # caller environment
    p2 = (
        ggplot(data, aes(x="x", y="y"))
        + geom_point(alpha=0.5)
        + geom_quantile(
            quantiles=[0.001, 0.5, 0.999], formula="y~np.absolute(x)", size=2
        )
    )

    # Two (.001, .999) quantile lines should bound the points
    # from below and from above, and the .5 line should go
    # through middle (approximately).
    assert p == "lines"
    assert p2 == "lines"
