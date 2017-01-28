from __future__ import absolute_import, division, print_function
from textwrap import dedent
from collections import OrderedDict

import numpy as np
import six


def indent(txt, level=1):
    """
    Indent text
    """
    tpl = ' '*(level*4) + '{}'
    lines = [tpl.format(line) for line in txt.split('\n')]
    return '\n'.join(lines)


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


def get_geom_documentation(geom):
    """
    Create a structured documentation for the geom
    """
    if (geom.__doc__ is None or
            '{documentation}' not in geom.__doc__):
        return ''

    def usage():
        name = geom.__name__
        line1 = ("{name}(mapping=None, data=None, stat='{stat}', "
                 "position='{position}', ").format(
                 name=name,
                 stat=geom.DEFAULT_PARAMS['stat'],
                 position=geom.DEFAULT_PARAMS['position'])

        line2 = ("show_legend={show_legend}, inherit_aes={inherit_aes}, "
                 "**kwargs)").format(
                     indent=' '*(len(name)+1),
                     show_legend=geom.DEFAULT_PARAMS.get('show_legend', None),
                     inherit_aes=geom.DEFAULT_PARAMS.get('inherit_aes', True))

        out = """
        .. rubric:: Usage

        ::

            {line1}
            {indent}{line2}

        Only the ``mapping`` and ``data`` can be positional, the
        ``**kwargs`` can be aesthetics (or parameters) used by ``geom``,
        or if the ``geom`` does not recognise them, they are passed on to
        the ``stat``.
        """.format(indent=' '*(len(name)+1),
                   line1=line1,
                   line2=line2)
        return out

    def aesthetics():
        contents = OrderedDict(('**{}**'.format(ae), '')
                               for ae in sorted(geom.REQUIRED_AES))
        contents.update(sorted(geom.DEFAULT_AES.items()))
        table = dict_to_table(('Aesthetic', 'Default value'),
                              contents)
        table = indent(table, 2)
        out = """
        .. rubric:: Aesthetics \n\n{table}\n

        The **bold** aesthetics are required.
        """.format(table=table)
        return out

    def parameters():
        params = OrderedDict(sorted(geom.DEFAULT_PARAMS.items()))
        table = dict_to_table(('Parameter', 'Default value'),
                              params)
        table = indent(table, 2)
        out = """
        .. rubric:: Parameters \n\n{table}\n
        """.format(table=table)
        return out

    return ''.join([usage(), aesthetics(), parameters()])


def get_stat_documentation(stat):
    """
    Create a structured documentation for the stat
    """
    if (stat.__doc__ is None or
            '{documentation}' not in stat.__doc__):
        return ''

    def usage():
        name = stat.__name__
        line1 = ("{name}(mapping=None, data=None, geom='{geom}', "
                 "position='{position}', ").format(
                     name=name,
                     geom=stat.DEFAULT_PARAMS['geom'],
                     position=stat.DEFAULT_PARAMS['position'])
        line2 = '**kwargs)'
        out = """
        .. rubric:: Usage

        ::

            {line1}
            {indent}{line2}

        Only the ``mapping`` and ``data`` can be positional, the
        ``**kwargs`` can be aesthetics (or parameters) used by ``stat``,
        or if the ``stat`` does not recognise them, they are passed on to
        the ``geom``.
        """.format(indent=' '*(len(name)+1),
                   line1=line1,
                   line2=line2)
        return out

    def aesthetics():
        contents = OrderedDict(('**{}**'.format(ae), '')
                               for ae in sorted(stat.REQUIRED_AES))
        contents.update(sorted(stat.DEFAULT_AES.items()))

        if not contents:
            return ''

        table = dict_to_table(('Aesthetic', 'Default value'),
                              contents)
        table = indent(table, 2)
        out = """
        .. rubric:: Aesthetics \n\n{table}\n

        The **bold** aesthetics are required.
        """.format(table=table)
        return out

    def parameters():
        params = OrderedDict(sorted(stat.DEFAULT_PARAMS.items()))
        table = dict_to_table(('Parameter', 'Default value'),
                              params)
        table = indent(table, 2)
        out = """
        .. rubric:: Parameters \n\n{table}\n
        """.format(table=table)
        return out

    return ''.join([usage(), aesthetics(), parameters()])


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
