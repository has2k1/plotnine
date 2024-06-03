from plotnine import position_stack
from plotnine.doctools import document
from plotnine.geoms.geom import geom
from plotnine.stats.stat import stat


@document
class geom_abc(geom):
    """
    Geom ABC

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {"color": None}
    DEFAULT_PARAMS = {
        "stat": "bin",
        "position": position_stack,
        "na_rm": False,
    }


def test_document_geom():
    doc = geom_abc.__doc__
    # assert "~plotnine.stats.stat_bin" in doc
    assert 'stat, default="bin"' in doc
    assert 'position, default="position_stack"' in doc


@document
class stat_abc(stat):
    """
    Stat ABC

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {"weight": None}
    DEFAULT_PARAMS = {"geom": geom_abc, "position": "stack", "na_rm": False}


def test_document_stat():
    doc = stat_abc.__doc__
    assert "geom_abc" in doc
    # assert "~plotnine.positions.position_stack" in doc
    assert 'position, default="stack"' in doc
