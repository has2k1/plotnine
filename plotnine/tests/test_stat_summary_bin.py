from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd

from plotnine import ggplot, aes, stat_summary_bin


df = pd.DataFrame({
    'xd': list('aaaaabbbbcccccc'),
    'xc': range(0, 15),
    'y': [1, 2, 3, 4, 5, 1.5, 1.5, 6, 6, 5, 5, 5, 5, 5, 5]})


def test_discrete_x():
    p = (ggplot(df, aes('xd', 'y'))
         + stat_summary_bin(fun_y=np.mean,
                            fun_ymin=np.min,
                            fun_ymax=np.max,
                            geom='bar'))

    assert p == 'discrete_x'


def test_continuous_x():
    p = (ggplot(df, aes('xc', 'y'))
         + stat_summary_bin(fun_y=np.mean,
                            fun_ymin=np.min,
                            fun_ymax=np.max,
                            bins=5,
                            geom='bar'))

    assert p == 'continuous_x'
