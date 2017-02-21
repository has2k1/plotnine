from __future__ import absolute_import, division, print_function
from textwrap import dedent, wrap
from collections import OrderedDict

import numpy as np
import six


# Parameter arguments that are listed first in the geom and
# stat class signatures

common_geom_params = ['mapping', 'data', 'stat', 'position',
                      'na_rm', 'inherit_aes', 'show_legend']
common_geom_param_values = {'mapping': None, 'data': None,
                            'inherit_aes': True, 'show_legend': None}

common_stat_params = ['mapping', 'data', 'geom', 'position']
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

AESTHETICS_TPL = """
.. rubric:: Aesthetics

{aesthetics_table}

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
default, includes any aesthetics that are mapped. :py:`False` never \
includes and :py:`True` always includes."""
}


GEOM_PARAMS_TPL = """\
mapping: aes, optional
    {mapping}
data: dataframe, optional
    {data}
stat: str or stat, optional (default: {default_stat})
    {stat}
position: str or position, optional (default: {default_position})
    {position}
na_rm: bool, optional (default: {default_na_rm})
    {na_rm}
inherit_aes: bool, optional (default: {default_inherit_aes})
    {inherit_aes}
show_legend: bool, optional (default: None)
    {show_legend}
"""

STAT_PARAMS_TPL = """\
mapping: aes, optional
    {mapping}
data: dataframe, optional
    {data}
geom: str or stat, optional (default: {default_geom})
    {stat}
position: str or position, optional (default: {default_position})
    {position}
"""


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
            if isinstance(value, six.string_types):
                value = "'{}'".format(value)
            value = ':py:`{}`'.format(value)
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
        if isinstance(value, six.string_types):
            value = "'{}'".format(value)
        tokens.append('{}={}'.format(key, value))

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
    s2_lines = wrap(s2, width=line_width, subsequent_indent=indent_spaces)
    return s1 + '\n'.join(s2_lines)


def get_geom_documentation(geom):
    """
    Create a structured documentation for the geom
    """
    # usage
    signature = make_signature(geom.__name__,
                               geom.DEFAULT_PARAMS,
                               common_geom_params,
                               common_geom_param_values)
    usage = GEOM_SIGNATURE_TPL.format(signature=signature)

    # common_parameters
    d = geom.DEFAULT_PARAMS
    common_parameters = GEOM_PARAMS_TPL.format(
        default_stat=d['stat'],
        default_position=d['position'],
        default_na_rm=d['na_rm'],
        default_inherit_aes=d.get('inherit_aes', True),
        **common_params_doc)

    # aesthetics
    contents = OrderedDict(('**{}**'.format(ae), '')
                           for ae in sorted(geom.REQUIRED_AES))
    contents.update(sorted(geom.DEFAULT_AES.items()))
    table = dict_to_table(('Aesthetic', 'Default value'),
                          contents)
    aesthetics = AESTHETICS_TPL.format(aesthetics_table=table)

    return usage, common_parameters, aesthetics


def get_stat_documentation(stat):
    """
    Create a structured documentation for the stat
    """
    # usage:
    signature = make_signature(stat.__name__,
                               stat.DEFAULT_PARAMS,
                               common_stat_params,
                               common_stat_param_values)
    usage = STAT_SIGNATURE_TPL.format(signature=signature)

    # common_parameters
    d = stat.DEFAULT_PARAMS
    common_parameters = STAT_PARAMS_TPL.format(
            default_geom=d['geom'],
            default_position=d['position'],
            **common_params_doc)

    # aesthetics
    contents = OrderedDict(('**{}**'.format(ae), '')
                           for ae in sorted(stat.REQUIRED_AES))
    contents.update(sorted(stat.DEFAULT_AES.items()))
    table = dict_to_table(('Aesthetic', 'Default value'),
                          contents)
    aesthetics = AESTHETICS_TPL.format(aesthetics_table=table)

    return usage, common_parameters, aesthetics


def document(klass):
    """
    Decorator to document a class

    It replaces `{usage}`, `{common_parameters}` and
    `{aesthetics}` with generated documentation.
    """
    docstring = klass.__doc__
    if docstring is None:
        return klass

    # Dedented so that it lineups (in sphinx) with the part
    # generated parts when put together
    docstring = dedent(docstring)

    if klass.__name__.startswith('geom'):
        func = get_geom_documentation
    elif klass.__name__.startswith('stat'):
        func = get_stat_documentation
    else:
        return klass

    usage, common_parameters, aesthetics = func(klass)
    docstring = docstring.replace('{usage}', usage)
    docstring = docstring.replace('{common_parameters}',
                                  common_parameters)
    docstring = docstring.replace('{aesthetics}', aesthetics)

    klass.__doc__ = docstring
    return klass
