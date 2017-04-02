from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_point, geom_quantile

n = 200  # Should not be too big, affects the test duration
random_state = np.random.RandomState(1234567890)
# points that diverge like a point flash-light
df = pd.DataFrame({'x': np.arange(n),
                   'y': np.arange(n) * (1 + random_state.rand(n))
                   })


def test_lines():
    p = (ggplot(df, aes(x='x', y='y')) +
         geom_point(alpha=.5) +
         geom_quantile(quantiles=[.001, .5, .999], formula='y~x',
                       size=2))

    # Two (.001, .999) quantile lines should bound the points
    # from below and from above, and the .5 line should go
    # through middle (approximately).
    assert p == 'lines'
