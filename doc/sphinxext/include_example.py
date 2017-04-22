# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import importlib

import nbformat
import sphinx
import nbsphinx
from docutils.parsers.rst.directives.misc import Include as BaseInclude
from nbconvert.writers import FilesWriter
from plotnine_examples.notebooks import NBPATH

package = importlib.import_module('plotnine')
base_path = os.path.dirname(package.__path__[0])


def get_notebook_filename(objname):
    """
    Return the notebook filename with examples for the object
    """
    filename = '{}/{}.ipynb'.format(NBPATH, objname)
    if not os.path.exists(filename):
        filename = ''
    return filename


def get_rst_filename(objname):
    """
    Return name of file (ReST) with examples
    """
    filename = '{}/doc/generated/{}_examples.txt'.format(
        base_path, objname)
    return filename


def notebook_to_rst(notebook_filename, rst_filename):
    """
    Execute notebook & convert it to rst

    Returns
    -------
    filename : str
        Full filename of the file with the ReST contents.
        The extension of the file is '.txt' since it will
        note be part of the `toctree`.
    """
    path = os.path.dirname(rst_filename)
    basename = os.path.splitext(os.path.basename(rst_filename))[0]
    resources_d = {
        'metadata': {'path': path},
        'output_files_dir': basename
    }

    # Read notebook
    with open(notebook_filename, 'r') as f:
        nb = nbformat.read(f, as_version=4)

    # Export
    rst_exporter = nbsphinx.Exporter(execute='never', allow_errors=True)
    (body, resources) = rst_exporter.from_notebook_node(
        nb, resources_d)

    # Correct path for the resources
    for filename in list(resources['outputs'].keys()):
        tmp = '{}/{}'.format(path, filename)
        resources['outputs'][tmp] = resources['outputs'].pop(filename)

    fw = FilesWriter()
    fw.build_directory = path
    # Prevent "not in doctree" complains
    resources['output_extension'] = '.txt'
    body = 'Examples\n--------\n' + body
    return fw.write(body, resources, notebook_name=basename)


def process_object(objname):
    """
    Return filename with the examples for the object

    Parameters
    ----------
    objname : str
        Name of ggplot object being documented
        e.g 'geom_point', 'facet_grid', ...
    """
    notebook_filename = get_notebook_filename(objname)
    if not os.path.exists(notebook_filename):
        return
    rst_filename = get_rst_filename(objname)
    return notebook_to_rst(notebook_filename, rst_filename)


class IncludeExamples(BaseInclude):
    """
    Directive to include examples for a named object
    """

    def run(self):
        objname = self.arguments[0]
        filename = process_object(objname)
        if not filename:
            return []
        self.arguments[0] = filename
        return BaseInclude.run(self)


def setup(app):
    app.add_directive('include_examples', IncludeExamples)
    return {'version': sphinx.__display_version__,
            'parallel_read_safe': True}
