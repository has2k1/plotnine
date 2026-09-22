import pytest

import plotnine.doctools as doctools
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


@pytest.mark.parametrize("next_section", ["Notes", "Computed Variables"])
def test_append_to_parameters_before_next_section(next_section):
    docstring = f"""\
Description

Parameters
----------
value : int
    Existing parameter.

{next_section}
{"-" * len(next_section)}
Section contents.
"""
    addition = "**kwargs : Any\n    Additional parameters.\n"
    expected = docstring.replace(
        f"\n{next_section}\n", f"{addition}\n{next_section}\n"
    )

    assert doctools.append_to_parameters(addition, docstring) == expected
