from __future__ import absolute_import, division, print_function

import pandas as pd
import numpy as np

from plotnine import ggplot, aes, geom_spoke, theme

n = 4
df = pd.DataFrame({
        'x': [1]*n,
        'y': range(n),
        'angle': np.linspace(0, np.pi/2, n),
        'radius': range(1, n+1),
        'z': range(n)
    })
_theme = theme(subplots_adjust={'right': 0.85})


def test_aesthetics():
    p = (ggplot(df, aes(y='y', angle='angle', radius='radius')) +
         geom_spoke(aes('x'), size=2) +
         geom_spoke(aes('x+2', alpha='z'), size=2) +
         geom_spoke(aes('x+4', linetype='factor(z)'), size=2) +
         geom_spoke(aes('x+6', color='factor(z)'), size=2) +
         geom_spoke(aes('x+8', size='z')))

    assert p + _theme == 'aesthetics'
