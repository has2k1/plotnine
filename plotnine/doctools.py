import re
from textwrap import indent, dedent, wrap
from functools import lru_cache

import numpy as np


# Parameter arguments that are listed first in the geom and
# stat class signatures

common_geom_params = [
    'mapping',
    'data',
    'stat',
    'position',
    'na_rm',
    'inherit_aes',
    'show_legend',
    'raster'
]
common_geom_param_values = {
    'mapping': None,
    'data': None,
    'inherit_aes': True,
    'show_legend': None,
    'raster': False
}

common_stat_params = ['mapping', 'data', 'geom', 'position', 'na_rm']
common_stat_param_values = common_geom_param_values

# Templates for docstrings

GEOM_SIGNATURE_TPL = """
.. rubric:: Usage

::

    {signature}

Only the ``mapping`` and ``data`` can be positional, the rest must
be keyword arguments. ``**kwargs`` can be aesthetics (or parameters)
used by the ``stat``.
"""

AESTHETICS_TABLE_TPL = """
{table}

The **bold** aesthetics are required.
"""

STAT_SIGNATURE_TPL = """
.. rubric:: Usage

::

    {signature}

Only the ``mapping`` and ``data`` can be positional, the rest must
be keyword arguments. ``**kwargs`` can be aesthetics (or parameters)
used by the ``geom``.
"""


common_params_doc = {
    'mapping': """\
Aesthetic mappings created with :meth:`~plotnine.aes`. If specified and \
:py:`inherit.aes=True`, it is combined with the default mapping for the plot. \
You must supply mapping if there is no plot mapping.""",

    'data': """\
The data to be displayed in this layer. If :py:`None`, the data from \
from the :py:`ggplot()` call is used. If specified, it overrides the \
data from the :py:`ggplot()` call.""",

    'stat': """\
The statistical transformation to use on the data for this layer. \
If it is a string, it must be the registered and known to Plotnine.""",

    'position': """\
Position adjustment. If it is a string, it must be registered and \
known to Plotnine.""",

    'na_rm': """\
If :py:`False`, removes missing values with a warning. If :py:`True` \
silently removes missing values.""",

    'inherit_aes': """\
If :py:`False`, overrides the default aesthetics.""",

    'show_legend': """\
Whether this layer should be included in the legends. :py:`None` the \
default, includes any aesthetics that are mapped. If a :class:`bool`, \
:py:`False` never includes and :py:`True` always includes. A \
:class:`dict` can be used to *exclude* specific aesthetis of the layer \
from showing in the legend. e.g :py:`show_legend={'color': False}`, \
any other aesthetic are included by default.""",

    'raster': """\
If ``True``, draw onto this layer a raster (bitmap) object even if\
the final image is in vector format."""
}


GEOM_PARAMS_TPL = """\
mapping : aes, optional
    {mapping}
    {_aesthetics_doc}
data : dataframe, optional
    {data}
stat : str or stat, optional (default: {default_stat})
    {stat}
position : str or position, optional (default: {default_position})
    {position}
na_rm : bool, optional (default: {default_na_rm})
    {na_rm}
inherit_aes : bool, optional (default: {default_inherit_aes})
    {inherit_aes}
show_legend : bool or dict, optional (default: None)
    {show_legend}
raster : bool, optional (default: {default_raster})
    {raster}
"""

STAT_PARAMS_TPL = """\
mapping : aes, optional
    {mapping}
    {_aesthetics_doc}
data : dataframe, optional
    {data}
geom : str or geom, optional (default: {default_geom})
    {stat}
position : str or position, optional (default: {default_position})
    {position}
na_rm : bool, optional (default: {default_na_rm})
    {na_rm}
"""

DOCSTRING_SECTIONS = {
    'parameters', 'see also', 'note', 'notes',
    'example', 'examples'}

PARAM_PATTERN = re.compile(r'\s*([_A-Za-z]\w*)\s:\s')


def dict_to_table(header, contents):
    """
    Convert dict to table

    Parameters
    ----------
    header : tuple
        Table header. Should have a length of 2.
    contents : dict
        The key becomes column 1 of table and the
        value becomes column 2 of table.
    """
    def to_text(row):
        name, value = row
        m = max_col1_size + 1 - len(name)
        spacing = ' ' * m

        return ''.join([name, spacing, value])

    thead = tuple(str(col) for col in header)
    rows = []
    for name, value in contents.items():
        # code highlighting
        if value != '':
            if isinstance(value, str):
                value = f"'{value}'"
            value = f':py:`{value}`'
        rows.append((name, value))

    n = np.max([len(header[0])] +
               [len(col1) for col1, _ in rows])
    hborder = tuple('='*n for col in header)
    rows = [hborder, thead, hborder] + rows + [hborder]
    max_col1_size = np.max([len(col1) for col1, _ in rows])
    table = '\n'.join([to_text(row) for row in rows])
    return table


def make_signature(name, params, common_params, common_param_values):
    """
    Create a signature for a geom or stat

    Gets the DEFAULT_PARAMS (params) and creates are comma
    separated list of the `name=value` pairs. The common_params
    come first in the list, and they get take their values from
    either the params-dict or the common_geom_param_values-dict.
    """
    tokens = []
    seen = set()

    def tokens_append(key, value):
        if isinstance(value, str):
            value = f"'{value}'"
        tokens.append(f'{key}={value}')

    # preferred params come first
    for key in common_params:
        seen.add(key)
        try:
            value = params[key]
        except KeyError:
            value = common_param_values[key]
        tokens_append(key, value)

    # other params (these are the geom/stat specific parameters
    for key in (set(params) - seen):
        tokens_append(key, params[key])

    # name, 1 opening bracket, 4 spaces in SIGNATURE_TPL
    s1 = name + '('
    s2 = ', '.join(tokens) + ', **kwargs)'
    line_width = 78 - len(s1)
    indent_spaces = ' ' * (len(s1) + 4)
    newline_and_space = '\n' + indent_spaces
    s2_lines = wrap(s2, width=line_width)
    return s1 + newline_and_space.join(s2_lines)


@lru_cache(maxsize=256)
def docstring_section_lines(docstring, section_name):
    """
    Return a section of a numpydoc string

    Paramters
    ---------
    docstring : str
        Docstring
    section_name : str
        Name of section to return

    Returns
    -------
    section : str
        Section minus the header
    """
    lines = []
    inside_section = False
    underline = '-' * len(section_name)
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
    return '\n'.join(lines)


def docstring_parameters_section(obj):
    """
    Return the parameters section of a docstring
    """
    return docstring_section_lines(obj.__doc__, 'parameters')


def param_spec(line):
    """
    Identify and return parameter

    Parameters
    ----------
    line : str
        A line in the parameter section.

    Returns
    -------
    name : str or None
        Name of the parameter if the line for the parameter
        type specification and None otherwise.

    Examples
    --------
    >>> param_spec('line : str')
    breaks
    >>> param_spec("    A line in the parameter section.")
    """
    m = PARAM_PATTERN.match(line)
    if m:
        return m.group(1)


def parameters_str_to_dict(param_section):
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
        is of the form ``{param: all_parameter_text}``.
        You can reconstruct the ``param_section`` from the
        keys of the dictionary.

    See Also
    --------
    :func:`parameters_dict_to_str`
    """
    d = {}
    previous_param = None
    param_desc = None
    for line in param_section.split('\n'):
        param = param_spec(line)
        if param:
            if previous_param:
                d[previous_param] = '\n'.join(param_desc)
            param_desc = [line]
            previous_param = param
        elif param_desc:
            param_desc.append(line)

    if previous_param:
        d[previous_param] = '\n'.join(param_desc)

    return d


def parameters_dict_to_str(d):
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
    :func:`parameters_str_to_dict`
    """
    return '\n'.join(d.values())


def qualified_name(s, prefix):
    """
    Return the qualified name of s

    Only if s does not start with the prefix

    Examples
    --------
    >>> qualified_name('bin', 'stat_')
    '~plotnine.stats.stat_bin'
    >>> qualified_name('point', 'geom_')
    '~plotnine.geoms.geom_point'
    >>> qualified_name('stack', 'position_')
    '~plotnine.positions.position_'
    """
    lookup = {
        'stat_': '~plotnine.stats.stat_',
        'geom_': '~plotnine.geoms.geom_',
        'position_': '~plotnine.positions.position_'
    }
    if isinstance(s, str):
        if not s.startswith(prefix) and prefix in lookup:
            pre = lookup[prefix]
            s = f'{pre}{s}'
    elif isinstance(s, type):
        s = s.__name__
    else:
        s = s.__class__.__name__
    return s


def document_geom(geom):
    """
    Create a structured documentation for the geom

    It replaces `{usage}`, `{common_parameters}` and
    `{aesthetics}` with generated documentation.
    """
    # Dedented so that it lineups (in sphinx) with the part
    # generated parts when put together
    docstring = dedent(geom.__doc__)

    # usage
    signature = make_signature(geom.__name__,
                               geom.DEFAULT_PARAMS,
                               common_geom_params,
                               common_geom_param_values)
    usage = GEOM_SIGNATURE_TPL.format(signature=signature)

    # aesthetics
    contents = {
        f'**{ae}**': ''
        for ae in sorted(geom.REQUIRED_AES)
    }
    if geom.DEFAULT_AES:
        d = geom.DEFAULT_AES.copy()
        d['group'] = ''  # All geoms understand the group aesthetic
        contents.update(sorted(d.items()))

    table = dict_to_table(('Aesthetic', 'Default value'), contents)
    aesthetics_table = AESTHETICS_TABLE_TPL.format(table=table)
    tpl = dedent(geom._aesthetics_doc.lstrip('\n'))
    aesthetics_doc = tpl.format(aesthetics_table=aesthetics_table)
    aesthetics_doc = indent(aesthetics_doc, ' '*4)

    # common_parameters
    d = geom.DEFAULT_PARAMS
    common_parameters = GEOM_PARAMS_TPL.format(
        default_stat=qualified_name(d['stat'], 'stat_'),
        default_position=qualified_name(d['position'], 'position_'),
        default_na_rm=d['na_rm'],
        default_inherit_aes=d.get('inherit_aes', True),
        default_raster=d.get('raster', False),
        _aesthetics_doc=aesthetics_doc,
        **common_params_doc)

    docstring = docstring.replace('{usage}', usage)
    docstring = docstring.replace('{common_parameters}',
                                  common_parameters)
    geom.__doc__ = docstring
    return geom


def document_stat(stat):
    """
    Create a structured documentation for the stat

    It replaces `{usage}`, `{common_parameters}` and
    `{aesthetics}` with generated documentation.
    """
    # Dedented so that it lineups (in sphinx) with the part
    # generated parts when put together
    docstring = dedent(stat.__doc__)

    # usage:
    signature = make_signature(stat.__name__,
                               stat.DEFAULT_PARAMS,
                               common_stat_params,
                               common_stat_param_values)
    usage = STAT_SIGNATURE_TPL.format(signature=signature)

    # aesthetics
    contents = {
        f'**{ae}**': ''
        for ae in sorted(stat.REQUIRED_AES)
    }
    contents.update(sorted(stat.DEFAULT_AES.items()))
    table = dict_to_table(('Aesthetic', 'Default value'), contents)
    aesthetics_table = AESTHETICS_TABLE_TPL.format(table=table)
    tpl = dedent(stat._aesthetics_doc.lstrip('\n'))
    aesthetics_doc = tpl.format(aesthetics_table=aesthetics_table)
    aesthetics_doc = indent(aesthetics_doc, ' '*4)

    # common_parameters
    d = stat.DEFAULT_PARAMS
    common_parameters = STAT_PARAMS_TPL.format(
            default_geom=qualified_name(d['geom'], 'geom_'),
            default_position=qualified_name(d['position'], 'position_'),
            default_na_rm=d['na_rm'],
            _aesthetics_doc=aesthetics_doc,
            **common_params_doc)

    docstring = docstring.replace('{usage}', usage)
    docstring = docstring.replace('{common_parameters}',
                                  common_parameters)
    stat.__doc__ = docstring
    return stat


def document_scale(cls):
    """
    Create a documentation for a scale

    Import the superclass parameters

    It replaces `{superclass_parameters}` with the documentation
    of the parameters from the superclass.

    Parameters
    ----------
    cls : type
        A scale class

    Returns
    -------
    cls : type
        The scale class with a modified docstring.
    """
    params_list = []
    # Get set of cls params
    cls_param_string = docstring_parameters_section(cls)
    cls_param_dict = parameters_str_to_dict(cls_param_string)
    cls_params = set(cls_param_dict.keys())

    for i, base in enumerate(cls.__bases__):
        # Get set of base class params
        base_param_string = param_string = docstring_parameters_section(base)
        base_param_dict = parameters_str_to_dict(base_param_string)
        base_params = set(base_param_dict.keys())

        # Remove duplicate params from the base class
        duplicate_params = base_params & cls_params
        for param in duplicate_params:
            del base_param_dict[param]

        if duplicate_params:
            param_string = parameters_dict_to_str(base_param_dict)

        # Accumulate params of base case
        if i == 0:
            # Compensate for the indentation of the
            # {superclass_parameters} string
            param_string = param_string.strip()
        params_list.append(param_string)

        # Prevent the next base classes from bringing in the
        # same parameters.
        cls_params |= base_params

    # Fill in the processed superclass parameters
    superclass_parameters = '\n'.join(params_list)
    cls.__doc__ = cls.__doc__.format(
        superclass_parameters=superclass_parameters)
    return cls


DOC_FUNCTIONS = {
    'geom': document_geom,
    'stat': document_stat,
    'scale': document_scale
}


def document(cls):
    """
    Decorator to document a class
    """
    if cls.__doc__ is None:
        return cls

    baseclass_name = cls.mro()[-2].__name__

    try:
        return DOC_FUNCTIONS[baseclass_name](cls)
    except KeyError:
        return cls
