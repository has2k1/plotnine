from __future__ import annotations

import itertools
import os
import re
import typing
from functools import lru_cache
from textwrap import dedent, indent

if typing.TYPE_CHECKING:
    from typing import Any, Sequence, Type, TypeVar

    from plotnine.geoms.geom import geom
    from plotnine.stats.stat import stat

    T = TypeVar("T")

# Markup that is robust for documentation needs grid tables
# using tabulate and it is only required when
# building documentation.
try:
    from tabulate import tabulate as table_function
except ImportError:
    from ._utils import simple_table as table_function


# Parameter arguments that are listed first in the geom and
# stat class signatures

common_geom_params = [
    "mapping",
    "data",
    "stat",
    "position",
    "na_rm",
    "inherit_aes",
    "show_legend",
    "raster",
]
common_geom_param_values = {
    "mapping": None,
    "data": None,
    "inherit_aes": True,
    "show_legend": None,
    "raster": False,
}

common_stat_params = ["mapping", "data", "geom", "position", "na_rm"]
common_stat_param_values = common_geom_param_values

# Templates for docstrings

GEOM_SIGNATURE_TPL = """
**Usage**

{signature}

""".strip()

AESTHETICS_TABLE_TPL = """
{table}

The **bold** aesthetics are required."""

STAT_SIGNATURE_TPL = """
**Usage**

{signature}

""".strip()

common_params_doc = {
    "mapping": """\
Aesthetic mappings created with [aes](:class:`plotnine.mapping.aes`). If \
specified and `inherit_aes=True`{.py}, it is combined with the default \
mapping for the plot. You must supply mapping if there is no plot mapping.""",
    "data": """\
The data to be displayed in this layer. If `None`{.py}, the data from \
from the `ggplot()`{.py} call is used. If specified, it overrides the \
data from the `ggplot()`{.py} call.""",
    "stat": """\
The statistical transformation to use on the data for this layer. \
If it is a string, it must be the registered and known to Plotnine.""",
    "position": """\
Position adjustment. If it is a string, it must be registered and \
known to Plotnine.""",
    "na_rm": """\
If `False`{.py}, removes missing values with a warning. If `True`{.py} \
silently removes missing values.""",
    "inherit_aes": """\
If `False`{.py}, overrides the default aesthetics.""",
    "show_legend": """\
Whether this layer should be included in the legends. `None`{.py} the \
default, includes any aesthetics that are mapped. If a [](:class:`bool`), \
`False`{.py} never includes and `True`{.py} always includes. A \
[](:class:`dict`) can be used to *exclude* specific aesthetis of the layer \
from showing in the legend. e.g `show_legend={'color': False}`{.py}, \
any other aesthetic are included by default.""",
    "raster": """\
If `True`, draw onto this layer a raster (bitmap) object even if\
the final image is in vector format.""",
}


GEOM_PARAMS_TPL = """
mapping : ~plotnine.mapping.aes, default=None
    {mapping}
    {_aesthetics_doc}
data : ~pandas.DataFrame, default=None
    {data}
stat : str | ~plotnine.stats.stat.stat, default="{default_stat}"
    {stat}
position : str | ~plotnine.positions.position.position, \
default="{default_position}"
    {position}
na_rm : bool, default={default_na_rm}
    {na_rm}
inherit_aes : bool, default={default_inherit_aes}
    {inherit_aes}
show_legend : bool | dict, default=None
    {show_legend}
raster : bool, default={default_raster}
    {raster}
"""

STAT_PARAMS_TPL = """
mapping : ~plotnine.mapping.aes, default=None
    {mapping}
    {_aesthetics_doc}
data : ~pandas.DataFrame, default=None
    {data}
geom : str | ~plotnine.geoms.geom.geom, default="{default_geom}"
    {stat}
position : str | ~plotnine.positions.position.position, \
default="{default_position}"
    {position}
na_rm : bool, default={default_na_rm}
    {na_rm}
"""

geom_kwargs = """\
**kwargs: Any
    Aesthetics or parameters used by the `stat`.
"""

stat_kwargs = """\
**kwargs: Any
    Aesthetics or parameters used by the `geom`.
"""

DOCSTRING_SECTIONS = {
    "parameters",
    "see also",
    "note",
    "notes",
    "example",
    "examples",
}

PARAM_PATTERN = re.compile(r"\s*" r"([_A-Za-z]\w*)" r"\s:\s")
SECTIONS_PATTERN = re.compile(
    r"\n(?P<section>(?:\w+|(\w+\s\w+)+))\s*"  # section name
    r"\n-{3,}\n",  # underline
)
GENERATING_QUARTODOC = os.environ.get("GENERATING_QUARTODOC")


def dict_to_table(header: tuple[str, str], contents: dict[str, str]) -> str:
    """
    Convert dict to an (n x 2) table

    Parameters
    ----------
    header : tuple
        Table header. Should have a length of 2.
    contents : dict
        The key becomes column 1 of table and the
        value becomes column 2 of table.

    Examples
    --------
    >>> d = {"alpha": 1, "color": "blue", "fill": None}
    >>> print(dict_to_table(("Aesthetic", "Default Value"), d))
    Aesthetic  Default Value
    ---------  -------------
    alpha      `1`
    color      `'blue'`
    fill       `None`
    """
    rows = [
        (name, value if value == "" else f"`{value!r}`" "{.py}")
        for name, value in contents.items()
    ]
    return table_function(rows, headers=header, tablefmt="grid")


def make_signature(
    name: str,
    params: dict[str, Any],
    common_params: Sequence[str],
    common_param_values: dict[str, Any],
) -> str:
    """
    Create a signature for a geom or stat

    Gets the DEFAULT_PARAMS (params) and creates are comma
    separated list of the `name=value` pairs. The common_params
    come first in the list, and they get take their values from
    either the params-dict or the common_geom_param_values-dict.
    """
    params_lst = []
    _common_params_lookup = set(common_params)
    it = itertools.chain(
        common_params, (p for p in params if p not in _common_params_lookup)
    )

    # preferred params come first
    for i, key in enumerate(it):
        value = params.get(key, common_param_values.get(key))
        if isinstance(value, str):
            value = f'"{value}"'
        params_lst.append(f"{key}={value}")
        if i == 1:
            params_lst.append("*")

    params_lst.append("**kwargs")

    # Format to a maximum width of 78 chars
    # It fails when a parameter declarations is longer than 78
    opening = f"{name}("
    params_string = ", ".join(params_lst)
    closing = ")"
    pad = " " * 4
    if len(opening) + len(params_string) > 78:
        line_pad = f"\n{pad}"
        # One parameter per line
        if len(params_string) > 74:
            params_string = f",{line_pad}".join(params_lst)
        params_string = f"{line_pad}{params_string}"
        closing = f"\n{closing}"
    sig = f"{opening}{params_string}{closing}"
    return indent(sig, pad)


@lru_cache(maxsize=256)
def docstring_section_lines(docstring: str, section_name: str) -> str:
    """
    Return a section of a numpydoc string

    Parameters
    ----------
    docstring :
        Docstring
    section_name :
        Name of section to return

    Returns
    -------
    :
        Section minus the header
    """
    lines = []
    inside_section = False
    underline = "-" * len(section_name)
    expect_underline = False
    for line in docstring.splitlines():
        _line = line.strip().lower()

        if expect_underline:
            expect_underline = False
            if _line == underline:
                inside_section = True
                continue

        if _line == section_name:
            expect_underline = True
        elif _line in DOCSTRING_SECTIONS:
            # next section
            break
        elif inside_section:
            lines.append(line)
    return "\n".join(lines)


def append_to_section(s: str, docstring: str, section: str) -> str:
    """
    Append string s to a section in the docstring
    """
    idx = -1
    found = False
    for m in SECTIONS_PATTERN.finditer(docstring):
        if section == m.group("section"):
            found = True
        elif found:
            idx = m.start()
            break

    if found:
        if idx == -1:
            s = f"\n{s}"
        top, bottom = docstring[:idx], docstring[idx:]
        docstring = f"{top}{s}{bottom}"

    return docstring


def docstring_parameters_section(obj: Any) -> str:
    """
    Return the parameters section of a docstring
    """
    return docstring_section_lines(obj.__doc__, "parameters")


def param_spec(line: str) -> str | None:
    """
    Identify and return parameter

    Parameters
    ----------
    line : str
        A line in the parameter section.

    Returns
    -------
    name : str | None
        Name of the parameter if the line for the parameter
        type specification and None otherwise.

    Examples
    --------
    >>> param_spec('line : str')
    breaks
    >>> param_spec("    A line in the parameter section.")
    """
    m = PARAM_PATTERN.match(line)
    return m.group(1) if m else None


def parameters_str_to_dict(param_section: str) -> dict[str, str]:
    """
    Convert a param section to a dict

    Parameters
    ----------
    param_section : str
        Text in the parameter section

    Returns
    -------
    d : dict
        Dictionary of the parameters in the order that they
        are described in the parameters section. The dict
        is of the form `{param: all_parameter_text}`.
        You can reconstruct the `param_section` from the
        keys of the dictionary.

    See Also
    --------
    plotnine.doctools.parameters_dict_to_str
    """
    d = {}
    previous_param = ""
    param_desc: Sequence[str] = []
    for line in param_section.split("\n"):
        param = param_spec(line)
        if param:
            if previous_param:
                d[previous_param] = "\n".join(param_desc)
            param_desc = [line]
            previous_param = param
        elif param_desc:
            param_desc.append(line)

    if previous_param:
        d[previous_param] = "\n".join(param_desc)

    return d


def parameters_dict_to_str(d: dict[str, str]) -> str:
    """
    Convert a dict of param section to a string

    Parameters
    ----------
    d : dict
        Parameters and their descriptions in a docstring

    Returns
    -------
    param_section : str
        Text in the parameter section

    See Also
    --------
    plotnine.doctools.parameters_str_to_dict
    """
    return "\n".join(d.values())


def default_class_name(s: str | type | object) -> str:
    """
    Return the qualified name of s

    Only if s does not start with the prefix

    Examples
    --------
    >>> qualified_name('stat_bin')
    'stat_bin'
    >>> qualified_name(stat_bin)
    'stat_bin'
    >>> qualified_name(stat_bin())
    'stat_bin'
    """
    if isinstance(s, str):
        return s
    elif isinstance(s, type):
        s = s.__name__
    else:
        s = s.__class__.__name__
    return s


def document_geom(geom: type[geom]) -> type[geom]:
    """
    Create a structured documentation for the geom

    It replaces `{usage}`, `{common_parameters}` and
    `{aesthetics}` with generated documentation.
    """
    docstring = dedent(geom.__doc__ or "")
    docstring = append_to_section(geom_kwargs, docstring, "Parameters")

    # usage
    signature = make_signature(
        geom.__name__,
        geom.DEFAULT_PARAMS,
        common_geom_params,
        common_geom_param_values,
    )
    usage = GEOM_SIGNATURE_TPL.format(signature=signature)

    # aesthetics
    contents = {f"**{ae}**": "" for ae in sorted(geom.REQUIRED_AES)}
    if geom.DEFAULT_AES:
        d = geom.DEFAULT_AES.copy()
        d["group"] = ""  # All geoms understand the group aesthetic
        contents.update(sorted(d.items()))

    table = dict_to_table(("Aesthetic", "Default value"), contents)
    aesthetics_table = AESTHETICS_TABLE_TPL.format(table=table)
    tpl = dedent(geom._aesthetics_doc).strip()
    aesthetics_doc = tpl.format(aesthetics_table=aesthetics_table)
    aesthetics_doc = indent(aesthetics_doc, " " * 4)

    # common_parameters
    d = geom.DEFAULT_PARAMS
    common_parameters = GEOM_PARAMS_TPL.format(
        default_stat=default_class_name(d["stat"]),
        default_position=default_class_name(d["position"]),
        default_na_rm=d["na_rm"],
        default_inherit_aes=d.get("inherit_aes", True),
        default_raster=d.get("raster", False),
        _aesthetics_doc=aesthetics_doc,
        **common_params_doc,
    ).strip()

    docstring = docstring.replace("{usage}", usage)
    docstring = docstring.replace("{common_parameters}", common_parameters)
    geom.__doc__ = docstring
    return geom


def document_stat(stat: type[stat]) -> type[stat]:
    """
    Create a structured documentation for the stat

    It replaces `{usage}`, `{common_parameters}` and
    `{aesthetics}` with generated documentation.
    """
    # Dedented so that it lineups (in sphinx) with the part
    # generated parts when put together
    docstring = dedent(stat.__doc__ or "")
    docstring = append_to_section(stat_kwargs, docstring, "Parameters")

    # usage:
    signature = make_signature(
        stat.__name__,
        stat.DEFAULT_PARAMS,
        common_stat_params,
        common_stat_param_values,
    )
    usage = STAT_SIGNATURE_TPL.format(signature=signature)

    # aesthetics
    contents = {f"**{ae}**": "" for ae in sorted(stat.REQUIRED_AES)}
    contents.update(sorted(stat.DEFAULT_AES.items()))
    table = dict_to_table(("Aesthetic", "Default value"), contents)
    aesthetics_table = AESTHETICS_TABLE_TPL.format(table=table)
    tpl = dedent(stat._aesthetics_doc).strip()
    aesthetics_doc = tpl.replace("{aesthetics_table}", aesthetics_table)
    aesthetics_doc = indent(aesthetics_doc, " " * 4)

    # common_parameters
    d = stat.DEFAULT_PARAMS
    common_parameters = STAT_PARAMS_TPL.format(
        default_geom=default_class_name(d["geom"]),
        default_position=default_class_name(d["position"]),
        default_na_rm=d["na_rm"],
        _aesthetics_doc=aesthetics_doc,
        **common_params_doc,
    ).strip()

    docstring = docstring.replace("{usage}", usage)
    docstring = docstring.replace("{common_parameters}", common_parameters)
    stat.__doc__ = docstring
    return stat


DOC_FUNCTIONS = {
    "geom": document_geom,
    "stat": document_stat,
}


def document(cls: Type[T]) -> Type[T]:
    """
    Document a plotnine class

    To be used as a decorator
    """
    if cls.__doc__ is None:
        return cls

    baseclass_name = cls.mro()[-3].__name__

    try:
        return DOC_FUNCTIONS[baseclass_name](cls)
    except KeyError:
        return cls
