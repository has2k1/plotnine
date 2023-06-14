import pandas as pd
import pytest

from plotnine import aes, geom_point, ggplot, stat_identity
from plotnine.exceptions import PlotnineError
from plotnine.geoms.geom import geom

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
        geom_abc(do_the_impossible=True)


def test_geom_from_stat():
    stat = stat_identity(geom="point")
    assert isinstance(geom.from_stat(stat), geom_point)

    stat = stat_identity(geom="geom_point")
    assert isinstance(geom.from_stat(stat), geom_point)

    stat = stat_identity(geom=geom_point())
    assert isinstance(geom.from_stat(stat), geom_point)

    stat = stat_identity(geom=geom_point)
    assert isinstance(geom.from_stat(stat), geom_point)
