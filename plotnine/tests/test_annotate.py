from __future__ import absolute_import, division, print_function

import pandas as pd

from plotnine import ggplot, aes, geom_point, annotate

n = 4
df = pd.DataFrame({'x': range(n),
                   'y': range(n)})


def test_multiple_annotation_geoms():
    p = (ggplot(df, aes('x', 'y')) +
         geom_point() +
         annotate('point', 0, 1, color='red', size=5) +
         annotate('text', 1, 2, label='Text', color='red',
                  size=15, angle=45) +
         annotate('rect', xmin=1.8, xmax=2.2, ymin=2.8,
                  ymax=3.2, size=1, color='red', alpha=0.3) +
         annotate('segment', x=2.8, y=3.8, xend=3.2,
                  yend=4.2, color='red', size=1))

    assert p == 'multiple_annotation_geoms'
