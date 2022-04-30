import pandas as pd
import pytest

from plotnine import ggplot, aes, geom_point, geom_rect, geom_segment, annotate
from plotnine.exceptions import PlotnineError

n = 4
df = pd.DataFrame({'x': range(n),
                   'y': range(n)})


def test_multiple_annotation_geoms():
    p = (ggplot(df, aes('x', 'y')) +
         geom_point() +
         annotate('point', 0, 1, color='red', size=5) +
         annotate('text', 1, 2, label='Text', color='red',
                  size=15, angle=45) +
         annotate(geom_rect, xmin=1.8, xmax=2.2, ymin=2.8,
                  ymax=3.2, size=1, color='red', alpha=0.3) +
         annotate(geom_segment, x=2.8, y=3.8, xend=3.2,
                  yend=4.2, color='red', size=1))
    assert p == 'multiple_annotation_geoms'


def test_non_geom_raises():
    with pytest.raises(PlotnineError):
        annotate('doesnotexist', x=1)

    with pytest.raises(PlotnineError):
        annotate(5)

    class NotAGeom():
        pass

    with pytest.raises(PlotnineError):
        annotate(NotAGeom)

    with pytest.raises(PlotnineError):
        annotate(geom_point())
