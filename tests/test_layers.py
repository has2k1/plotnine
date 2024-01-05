from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from plotnine import aes, geom_path, geom_point, ggplot
from plotnine.exceptions import PlotnineError, PlotnineWarning
from plotnine.layer import Layers, layer

data = pd.DataFrame({"x": range(10), "y": range(10)})
colors = ["red", "green", "blue"]

n = 5000
prg = np.random.RandomState(123)
larger_data = pd.DataFrame(
    {"x": prg.uniform(1, 1000, size=n), "y": prg.uniform(1, 1000, size=n)}
)


def _get_colors(p):
    return [l.geom.aes_params["color"] for l in p.layers]


class TestLayers:
    # Give each geom in the layer a different color which we
    # can used to test the ordering.
    lyrs = Layers(
        [
            geom_point(color=colors[0]),
            geom_point(color=colors[1]),
            geom_point(color=colors[2]),
        ]
    )

    def test_addition(self):
        p = ggplot(data, aes("x", "y"))
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
        p = ggplot(data, aes("x", "y"))

        _lyrs = self.lyrs[1:]
        assert isinstance(_lyrs, Layers)

        p1 = p + self.lyrs[0] + self.lyrs[2]
        assert _get_colors(p1) == colors[::2]

        p2 = p + self.lyrs[::2]
        assert _get_colors(p2) == colors[::2]

        p3 = p + (self.lyrs[:1] + self.lyrs[2:])
        assert _get_colors(p3) == colors[::2]


def test_inserting_layers():
    class as_first_layer:
        def __init__(self, obj):
            self.obj = obj

        def __radd__(self, plot):
            plot.layers.insert(0, self.obj.to_layer())
            return plot

        def __rsub__(self, plot):
            return self.__radd__(plot)

    p = (
        ggplot(data, aes("x", "y"))
        + geom_point(size=4)
        + as_first_layer(geom_point(color="cyan", size=8))
        - as_first_layer(geom_point(color="red", size=12))
    )

    assert p == "inserting_layers"


def test_layer_with_nodata():
    # no data but good mappings
    p = ggplot() + geom_point(aes([1, 2], [1, 2]))
    p.build_test()

    # no data, and unresolvable mappings
    p = ggplot(aes("x", "y")) + geom_point()
    with pytest.raises(PlotnineError) as pe:
        p.draw_test()

    assert "Could not evaluate the 'x' mapping:" in pe.value.message


class TestRasterizing:
    p = ggplot(larger_data, aes("x", "y"))

    def _assert_raster_smaller(self, p_no_raster, p_raster):
        # Plot and check that the file sizes are smaller when
        # rastering. Then delete the files.
        geom_name = p_raster.layers[0].geom.__class__.__name__
        fn1 = Path(f"{geom_name}-no-raster.pdf")
        fn2 = Path(f"{geom_name}-raster.pdf")

        try:
            with pytest.warns(PlotnineWarning):
                p_no_raster.save(fn1)
                p_raster.save(fn2)
            assert fn1.stat().st_size > fn2.stat().st_size
        finally:
            fn1.unlink(missing_ok=True)
            fn2.unlink(missing_ok=True)

    def test_geom_point(self):
        p1 = self.p + geom_point()
        p2 = self.p + geom_point(raster=True)
        self._assert_raster_smaller(p1, p2)

    def test_geom_path(self):
        p1 = self.p + geom_path()
        p2 = self.p + geom_path(raster=True)
        self._assert_raster_smaller(p1, p2)
