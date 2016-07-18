from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from .. import ggplot, aes, geom_density
from .conftest import cleanup

n = 6  # Some even number greater than 2

# ladder: 0 1 times, 1 2 times, 2 3 times, ...
df = pd.DataFrame({'x': np.repeat(range(n+1), range(n+1)),
                   'z': np.repeat(range(n//2), range(3, n*2, 4))})


@cleanup
def test_basic():
    p = ggplot(df, aes('x', fill='factor(z)'))

    p1 = p + geom_density(kernel='gaussian', alpha=.3)
    p2 = p + geom_density(kernel='gaussian', alpha=.3, trim=True)
    p3 = p + geom_density(kernel='triangular', alpha=.3)  # other

    assert p1 == 'gaussian'
    assert p2 == 'gaussian-trimmed'
    assert p3 == 'triangular'
