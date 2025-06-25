from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

from plotnine import (
    aes,
    after_scale,
    after_stat,
    annotate,
    coord_trans,
    facet_null,
    geom_bar,
    geom_histogram,
    geom_line,
    geom_point,
    ggplot,
    ggtitle,
    guides,
    labs,
    lims,
    scale_x_continuous,
    stage,
    stat_identity,
    theme,
    theme_gray,
    xlab,
    xlim,
    ylab,
)
from plotnine.exceptions import PlotnineError, PlotnineWarning
from plotnine.mapping.aes import RepeatAesthetic

data = pd.DataFrame({"x": np.arange(10), "y": np.arange(10)})


def test_labels():
    """
    Test invalid arguments to chart components
    """
    gg = ggplot(data, aes(x="x", y="y"))
    gg = gg + geom_point()
    gg = gg + xlab("xlab")
    gg = gg + ylab("ylab")
    gg = gg + ggtitle("title")

    assert gg.labels.x == "xlab"
    assert gg.labels.y == "ylab"
    assert gg.labels.title == "title"

    gg = gg + labs(x="xlab2", y="ylab2", title="title2", caption="caption2")
    assert gg.labels.x == "xlab2"
    assert gg.labels.y == "ylab2"
    assert gg.labels.title == "title2"
    assert gg.labels.caption == "caption2"


def test_ggplot_parameters():
    p = ggplot(data, aes("x"))

    assert p.data is data
    assert p.mapping == aes("x")
    assert p.environment.namespace["np"] is np
    assert p.environment.namespace["pd"] is pd

    p = ggplot(data=data, mapping=aes("x"))
    assert p.data is data
    assert p.mapping == aes("x")

    p = ggplot(data=data)
    assert p.data is data
    assert p.mapping == aes()

    p = ggplot(mapping=aes("x"))
    assert p.data is None
    assert p.mapping == aes("x")

    p = ggplot()
    assert p.data is None
    assert p.mapping == aes()

    with pytest.raises(TypeError):
        ggplot([1, 2, 3], aes("x"))


def test_ggplot_parameters_grouped():
    p = data.groupby("x") >> ggplot(aes("x"))
    assert isinstance(p.data, pd.DataFrame)


def test_data_transforms():
    p = ggplot(aes(x="x", y="np.log(y+1)"), data)
    p = p + geom_point()
    p.draw_test()

    with pytest.raises(Exception):
        # no numpy available
        p = ggplot(aes(x="depth", y="ap.log(price)"), data)
        p = p + geom_point()
        p.draw_test()


def test_deepcopy():
    p = ggplot(data, aes("x")) + geom_histogram()
    p2 = deepcopy(p)
    assert p is not p2
    # Not sure what we have to do for that...
    assert p.data is p2.data
    assert len(p.layers) == len(p2.layers)
    assert p.layers[0].geom is not p2.layers[0].geom
    assert len(p.mapping) == len(p2.mapping)
    assert p.mapping is not p2.mapping
    assert p.environment == p2.environment
    assert p.environment is not p2.environment


def test_aes():
    result = aes("weight", "hp", color="qsec")
    expected = {"x": "weight", "y": "hp", "color": "qsec"}
    assert result == expected

    mapping = aes("weight", "hp", color=stage("qsec"))
    assert mapping["color"].start == "qsec"
    assert mapping._starting["color"] == "qsec"


def test_repeat_linetypes():
    repeat_ae = RepeatAesthetic.linetype
    assert repeat_ae("solid", 3) == ["solid", "solid", "solid"]
    assert repeat_ae("--", 3) == ["--", "--", "--"]
    assert repeat_ae((0, (3, 2)), 3) == [(0, (3, 2)), (0, (3, 2)), (0, (3, 2))]
    with pytest.raises(ValueError):
        repeat_ae("tada", 3)
    with pytest.raises(ValueError):
        repeat_ae((0, (3, 2.0)), 3)
    with pytest.raises(ValueError):
        repeat_ae((0, (3, 2, 1)), 2)


def test_repeat_shapes():
    repeat_ae = RepeatAesthetic.shape
    assert repeat_ae("o", 3) == ["o", "o", "o"]
    assert repeat_ae((4, 1, 45), 2) == [(4, 1, 45), (4, 1, 45)]


def test_repeat_colors():
    repeat_ae = RepeatAesthetic.color
    assert repeat_ae("red", 3) == ["red", "red", "red"]
    assert repeat_ae("#FF0000", 3) == ["#FF0000", "#FF0000", "#FF0000"]
    assert repeat_ae((1, 0, 0), 2) == [(1, 0, 0), (1, 0, 0)]
    assert repeat_ae((1, 0, 0, 0.5), 2) == [(1, 0, 0, 0.5), (1, 0, 0, 0.5)]


def test_calculated_aes():
    # after_stat('ae')
    mapping1 = aes("x", y=after_stat("density"))
    mapping2 = aes("x", y=after_stat("density*2"))
    mapping3 = aes("x", y=after_stat("density + count"))
    mapping4 = aes("x", y=after_stat("func(density)"))

    def _test():
        assert list(mapping1._calculated.keys()) == ["y"]
        assert list(mapping2._calculated.keys()) == ["y"]
        assert list(mapping3._calculated.keys()) == ["y"]
        assert list(mapping4._calculated.keys()) == ["y"]

        assert mapping1["y"].after_stat == "density"
        assert mapping2["y"].after_stat == "density*2"
        assert mapping3["y"].after_stat == "density + count"
        assert mapping4["y"].after_stat == "func(density)"

        assert mapping1._calculated["y"] == "density"
        assert mapping2._calculated["y"] == "density*2"
        assert mapping3._calculated["y"] == "density + count"
        assert mapping4._calculated["y"] == "func(density)"

    _test()

    # 'stat(ae)', DEPRECATED but still works
    mapping1 = aes("x", y="stat(density)")
    mapping2 = aes("x", y="stat(density*2)")
    mapping3 = aes("x", y="stat(density + count)")
    mapping4 = aes("x", y="stat(func(density))")
    _test()

    # '..ae..', DEPRECATED but still works
    mapping1 = aes("x", y="..density..")
    mapping2 = aes("x", y="..density..*2")
    mapping3 = aes("x", y="..density.. + ..count..")
    mapping4 = aes("x", y="func(..density..)")
    _test()

    data = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})
    p = ggplot(data) + geom_bar(aes(x="x", fill=after_stat("count + 2")))
    p.draw_test()

    p = ggplot(data) + geom_bar(aes(x="x", fill="stat(count + 2)"))
    p.draw_test()

    p = ggplot(data) + geom_bar(aes(x="x", fill="..count.. + 2"))
    p.draw_test()


def test_after_scale_mapping():
    data = pd.DataFrame({"x": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})
    data2 = pd.DataFrame(
        {
            # Same as above, but add 2 of each unique element
            "x": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4] + [1, 2, 3, 4] * 2
        }
    )

    p = ggplot(data) + geom_bar(aes(x="x", ymax=after_scale("ymax + 2")))
    p2 = ggplot(data2) + geom_bar(aes(x="x"))

    assert p + lims(y=(0, 7)) == "after_scale_mapping"
    assert p2 + lims(y=(0, 7)) == "after_scale_mapping"


def test_add_aes():
    data = pd.DataFrame({"var1": [1, 2, 3, 4], "var2": 2})
    p = ggplot(data) + geom_point()
    p += aes("var1", "var2")

    assert p.mapping == aes("var1", "var2")
    assert p.labels.x == "var1"
    assert p.labels.y == "var2"


def test_nonzero_indexed_data():
    data = pd.DataFrame(
        {98: {"blip": 0, "blop": 1}, 99: {"blip": 1, "blop": 3}}
    ).T
    p = ggplot(data, aes(x="blip", y="blop")) + geom_line()
    p.draw_test()


def test_inplace_add():
    p = _p = ggplot(data)

    p += aes("x", "y")
    assert p is _p

    p += geom_point()
    assert p is _p

    p += stat_identity()
    assert p is _p

    p += scale_x_continuous()
    assert p is _p

    with pytest.warns(PlotnineWarning):
        # Warning for; replacing existing scale added above
        p += xlim(0, 10)
        assert p is _p

    p += lims(y=(0, 10))
    assert p is _p

    p += labs(x="x")
    assert p is _p

    p += coord_trans()
    assert p is _p

    p += facet_null()
    assert p is _p

    p += annotate("point", 5, 5, color="red", size=5)
    assert p is _p

    p += guides()
    assert p is _p

    p += theme_gray()
    assert p is _p

    th = _th = theme_gray()
    th += theme(aspect_ratio=1)
    assert th is _th


def test_rrshift_piping():
    p = data >> ggplot(aes("x", "y")) + geom_point()
    assert p.data is data

    with pytest.raises(PlotnineError):
        data >> ggplot(data.copy(), aes("x", "y")) + geom_point()

    with pytest.raises(TypeError):
        "not a dataframe" >> ggplot(aes("x", "y")) + geom_point()


def test_rrshift_piping_grouped():
    p = data.groupby("x") >> ggplot(aes("x", "y")) + geom_point()
    assert p.data is data


def test_adding_list_ggplot():
    lst = [
        geom_point(),
        geom_point(aes("x+1", "y+1")),
        xlab("x-label"),
        coord_trans(),
    ]
    g = ggplot() + lst
    assert len(g.layers) == 2
    assert g.labels.x == "x-label"
    assert isinstance(g.coordinates, coord_trans)


def test_iadding_list_ggplot():
    lst = [
        geom_point(),
        geom_point(aes("x+1", "y+1")),
        xlab("x-label"),
        coord_trans(),
    ]
    g = ggplot()
    id_before = id(g)
    g += lst
    id_after = id(g)
    assert id_before == id_after
    assert len(g.layers) == 2
    assert g.labels.x == "x-label"
    assert isinstance(g.coordinates, coord_trans)


def test_adding_None():
    p = ggplot(data, aes("x", "y")) + geom_point()
    p2 = p + None
    assert p2 is not p
    assert isinstance(p2, ggplot)

    # Inplace addition
    p += None
    assert isinstance(p, ggplot)


def test_string_group():
    p = ggplot(data, aes("x", "y")) + geom_point(group="pi")
    p.draw_test()


def test_to_pandas():
    class SomeDataType:
        def to_pandas(self):
            return pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})

    data = SomeDataType()
    p1 = ggplot(data, aes("x", "y")) + geom_point()
    p2 = data >> ggplot(aes("x", "y")) + geom_point()
    assert p1 == "to_pandas"
    assert p2 == "to_pandas"


def test_callable_as_data():
    def _fn(data):
        return data.rename(columns={"xx": "x", "yy": "y"})

    data = pd.DataFrame({"xx": [1, 2, 3], "yy": [1, 2, 3]})
    p = ggplot(data, aes("x", "y")) + geom_point(_fn)
    p.draw_test()


def test_plotnine_all_imports():
    import plotnine as p9

    for name in p9.__all__:
        m = getattr(p9, name).__module__
        assert m.startswith("plotnine"), f"{m} in plotnine.__all__!"


def pickle_and_unpickle(obj):
    import io
    import pickle

    with io.BytesIO() as f:
        pickle.dump(obj, f)
        f.seek(0)
        unpickled_obj = pickle.load(f)

    return unpickled_obj


def test_pickle_ggplot():
    p = ggplot(data, aes("x", "y")) + geom_point()
    pickle_and_unpickle(p)


def test_pickle_matplotlib_figure():
    p = ggplot(data, aes("x", "y")) + geom_point()
    fig = p.draw()
    pickle_and_unpickle(fig)
