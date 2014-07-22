from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ggplot.tests import image_comparison

from ggplot import *

import numpy as np
import pandas as pd


@image_comparison(baseline_images=['default'])
def test_stat_summary_default():
    print(ggplot(aes(x='cut', y='carat'), data=diamonds)
          + stat_summary(fun_data = 'mean_cl_boot'))


@image_comparison(baseline_images=['fun_data'])
def test_stat_summary_own_fun_data():
    def median_quantile(series):
        return pd.Series({'y': np.median(series),
                          'ymin': np.percentile(series, 5),
                          'ymax': np.percentile(series, 95)})
    print(ggplot(aes(x='cut', y='carat'), data=diamonds)
          + stat_summary(fun_data = median_quantile))


@image_comparison(baseline_images=['fun_y'])
def test_stat_summary_own_fun_y():
    print(ggplot(aes(x='cut', y='carat'), data=diamonds)
          + stat_summary(fun_y = np.median, fun_ymin=np.min, fun_ymax=np.max))
