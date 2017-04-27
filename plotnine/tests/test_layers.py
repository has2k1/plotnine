import six
import pytest
import pandas as pd


from plotnine.layer import Layers, layer
from plotnine import ggplot, aes, geom_point
from plotnine.exceptions import PlotnineError


df = pd.DataFrame({'x': range(10),
                   'y': range(10)})
colors = ['red', 'green', 'blue']


def _get_colors(p):
    return [l.geom.aes_params['color'] for l in p.layers]


class TestLayers(object):
    # Give each geom in the layer a different color which we
    # can used to test the ordering.
    lyrs = Layers([
        geom_point(color=colors[0]),
        geom_point(color=colors[1]),
        geom_point(color=colors[2])
    ])

    def test_addition(self):
        p = ggplot(df, aes('x', 'y'))
        p1 = p + self.lyrs[0] + self.lyrs[1] + self.lyrs[2]
        assert _get_colors(p1) == colors

        p2 = p + self.lyrs
        assert _get_colors(p2) == colors

        # Real layers
        lyrs = Layers(layer.from_geom(obj) for obj in self.lyrs)
        p3 = p + lyrs
        assert _get_colors(p3) == colors

        p += self.lyrs
        assert _get_colors(p) == colors

        with pytest.raises(PlotnineError):
            geom_point() + layer.from_geom(geom_point())

        with pytest.raises(PlotnineError):
            geom_point() + self.lyrs

    def test_slicing(self):
        p = ggplot(df, aes('x', 'y'))

        p1 = p + self.lyrs[0] + self.lyrs[2]
        assert _get_colors(p1) == colors[::2]

        p2 = p + self.lyrs[::2]
        assert _get_colors(p2) == colors[::2]

        # Note: this will be broken for python 2 users
        if not six.PY2:
            p3 = p + (self.lyrs[:1] + self.lyrs[2:])
            assert _get_colors(p3) == colors[::2]
