# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import importlib

import nbformat
import sphinx
from docutils.parsers.rst.directives.misc import Include as BaseInclude
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import RSTExporter
from nbconvert.writers import FilesWriter

package = importlib.import_module('ggplot')
base_path = os.path.dirname(package.__path__[0])


def get_source_path(objname):
    """
    Return the source filename for the object
    """
    obj = getattr(package, objname)
    module_file = sys.modules[obj.__module__].__file__
    if module_file.endswith('.pyc'):
        module_file = module_file[:-1]
    return module_file


def get_notebook_filename(objname):
    """
    Return the notebook filename with examples for the object
    """
    filename = '{}/examples/{}.ipynb'.format(base_path, objname)
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
    basename = os.path.splitext(
        os.path.basename(rst_filename))[0]
    output_files_dir = basename
    resources_d = {'metadata': {'path': path},
                   'output_files_dir': output_files_dir}

    # Read notebook
    with open(notebook_filename, 'r') as f:
        nb = nbformat.read(f, as_version=4)

    # Execute
    ep = ExecutePreprocessor(kernel_name='python2')
    ep.preprocess(nb, resources_d)

    # Export
    rst_exporter = RSTExporter()
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
    src_filename = get_source_path(objname)
    notebook_filename = get_notebook_filename(objname)
    rst_filename = get_rst_filename(objname)
    filenames = (src_filename, notebook_filename, rst_filename)

    if not os.path.exists(notebook_filename):
        return

    if (os.path.exists(notebook_filename) and
            os.path.exists(rst_filename)):
        # If rst is uptodate
        mtimes = [os.stat(s).st_mtime for s in filenames]
        if (mtimes[0] < mtimes[2] and
                mtimes[1] < mtimes[2]):
            return rst_filename

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
