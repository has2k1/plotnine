import pandas as pd
import pytest

from plotnine import (
    aes,
    geom_col,
    geom_density,
    geom_histogram,
    geom_label,
    geom_line,
    geom_path,
    geom_point,
    geom_step,
    geom_text,
    ggplot,
    stat_identity,
)
from plotnine.exceptions import PlotnineError
from plotnine.geoms.geom import geom
from plotnine.layer import layer

data = pd.DataFrame({"col1": [1, 2, 3, 4], "col2": 2, "col3": list("abcd")})


def test_geom_basics():
    class geom_abc(geom):
        DEFAULT_AES = {"color": None}
        DEFAULT_PARAMS = {"stat": "identity", "position": "identity"}

    g = geom_abc(data=data)
    assert g.data is data

    g = geom_abc(data)
    assert g.data is data

    # geom data should not mess with the main data
    data_copy = data.copy()
    p = ggplot(data, aes("col", "mpg")) + geom_abc(data_copy)
    assert p.data is data
    assert p.layers[0].geom.data is data_copy

    g = geom_abc(aes(color="col1"))
    assert g.mapping["color"] == "col1"

    g = geom_abc(mapping=aes(color="col2"))
    assert g.mapping["color"] == "col2"

    # Multiple mappings
    with pytest.raises(TypeError):
        g = geom_abc(aes(color="col1"), aes(color="co1"))

    # setting, not mapping
    g = geom_abc(color="blue")
    assert g.aes_params["color"] == "blue"


def test_geom_with_invalid_argument():
    class geom_abc(geom):
        DEFAULT_AES = {"color": None}
        DEFAULT_PARAMS = {"stat": "identity", "position": "identity"}

    with pytest.raises(PlotnineError):
        layer(geom=geom_abc(do_the_impossible=True))


def test_default_params_inheritance():
    class geom_abc(geom):
        DEFAULT_PARAMS = {
            "stat": "identity",
            "position": "identity",
            "param1": 1,
        }

    class geom_xyz(geom_abc):
        DEFAULT_PARAMS = {"param2": 2}

    params = geom_xyz().params
    assert params["param1"] == 1  # from the parent
    assert params["param2"] == 2  # own declaration
    assert params["stat"] == "identity"
    assert params["position"] == "identity"
    assert params["na_rm"] is False  # from the base class

    # Real chains
    assert geom_step().params.keys() >= {
        "lineend",
        "linejoin",
        "arrow",
        "direction",
    }
    hist_params = geom_histogram().params
    assert hist_params["stat"] == "bin"
    assert "just" in hist_params
    assert "width" in hist_params
    assert geom_col().params["stat"] == "identity"
    assert geom_density().params["position"] == "identity"
    assert geom_label.default_params.keys() >= geom_text.default_params.keys()
    # No declaration of its own -> same view as the parent
    assert geom_line.default_params == geom_path.default_params


def test_geom_from_stat():
    stat = stat_identity(geom="point")
    assert isinstance(layer(stat=stat).geom, geom_point)

    stat = stat_identity(geom="geom_point")
    assert isinstance(layer(stat=stat).geom, geom_point)

    stat = stat_identity(geom=geom_point())
    assert isinstance(layer(stat=stat).geom, geom_point)

    stat = stat_identity(geom=geom_point)
    assert isinstance(layer(stat=stat).geom, geom_point)
