from __future__ import absolute_import, division, print_function
from textwrap import dedent, wrap
from collections import OrderedDict

import numpy as np
import six


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


def fillin_documentation(docstring, documentation_text):
    """
    Add documentation at '{documentation}'
    """
    if docstring is None:
        docstring = ''

    if '{documentation}' not in docstring:
        return docstring

    # All docstrings parts are dedented so that
    # they lineup (in sphinx) when put together
    new_docstring = dedent(docstring)
    documentation_text = dedent(documentation_text)

    # .format will fail if the documentation
    # contains a dict e.g x={'a': 3}. Plus
    # we expect a single documentation
    before, after = new_docstring.split('{documentation}')
    new_docstring = ''.join([before, documentation_text, after])

    return new_docstring


def make_signature(name, params, preferred, default_values):
    tokens = []
    seen = set()

    def tokens_append(key, value):
        if isinstance(value, six.string_types):
            value = "'{}'".format(value)
        tokens.append('{}={}'.format(key, value))

    # preferred params come first
    for key in preferred:
        seen.add(key)
        try:
            value = params[key]
        except KeyError:
            value = default_values[key]
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


def get_geom_documentation(geom):
    """
    Create a structured documentation for the geom
    """
    if (geom.__doc__ is None or
            '{documentation}' not in geom.__doc__):
        return ''

    def usage():
        preferred = ['mapping', 'data', 'stat', 'position',
                     'na_rm', 'inherit_aes', 'show_legend']
        default_values = {'mapping': None, 'data': None,
                          'inherit_aes': True, 'show_legend': None}
        signature = make_signature(geom.__name__, geom.DEFAULT_PARAMS,
                                   preferred, default_values)
        return GEOM_SIGNATURE_TPL.format(signature=signature)

    def aesthetics():
        contents = OrderedDict(('**{}**'.format(ae), '')
                               for ae in sorted(geom.REQUIRED_AES))
        contents.update(sorted(geom.DEFAULT_AES.items()))
        table = dict_to_table(('Aesthetic', 'Default value'),
                              contents)
        return AESTHETICS_TPL.format(aesthetics_table=table)

    return ''.join([usage(), aesthetics()])


def get_stat_documentation(stat):
    """
    Create a structured documentation for the stat
    """
    if (stat.__doc__ is None or
            '{documentation}' not in stat.__doc__):
        return ''

    def usage():
        preferred = ['mapping', 'data', 'geom', 'position']
        default_values = {'mapping': None, 'data': None,
                          'inherit_aes': True, 'show_legend': None}
        signature = make_signature(stat.__name__, stat.DEFAULT_PARAMS,
                                   preferred, default_values)
        return STAT_SIGNATURE_TPL.format(signature=signature)

    def aesthetics():
        contents = OrderedDict(('**{}**'.format(ae), '')
                               for ae in sorted(stat.REQUIRED_AES))
        contents.update(sorted(stat.DEFAULT_AES.items()))
        table = dict_to_table(('Aesthetic', 'Default value'),
                              contents)
        return AESTHETICS_TPL.format(aesthetics_table=table)

    return ''.join([usage(), aesthetics()])


def document(klass):
    """
    Decorator to document a class

    It replaces `{documentation}` with generated documentation.
    """
    documentation_text = ''
    if klass.__name__.startswith('geom'):
        documentation_text = get_geom_documentation(klass)

    if klass.__name__.startswith('stat'):
        documentation_text = get_stat_documentation(klass)

    if documentation_text:
        klass.__doc__ = fillin_documentation(
            klass.__doc__, documentation_text)
    return klass
