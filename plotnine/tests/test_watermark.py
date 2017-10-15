from __future__ import absolute_import, division, print_function
import os

import pandas as pd
from plotnine import ggplot, aes, geom_point, watermark


def test_watermark():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dir_path, 'images/plotnine-watermark.png')
    df = pd.DataFrame({'x': [1, 2, 3],
                       'y': [1, 2, 3]})
    p = (ggplot(df)
         + geom_point(aes('x', 'y'))
         + watermark(filename, 150, 160)
         + watermark(filename, 150, 210, 0.5)
         )

    assert p == 'watermark'
