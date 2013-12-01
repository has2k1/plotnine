#!/usr/bin/env python

"""
Python script for building documentation.

To build the docs you must have all optional dependencies for pandas
installed. See the installation instructions for a list of these.

Note: currently latex builds do not work because of table formats that are not
supported in the latex generation.

Usage
-----
python make.py clean
python make.py html
"""
from __future__ import print_function

import glob
import os
import shutil
import sys
import sphinx

os.environ['PYTHONPATH'] = '..'

SPHINX_BUILD = 'sphinxbuild'

       
def clean():
    if os.path.exists('build'):
        shutil.rmtree('build')

    if os.path.exists('generated'):
        shutil.rmtree('generated')


def html():
    check_build()
    if os.system('sphinx-build -P -b html -d build/doctrees '
                 '. build/html'):
        raise SystemExit("Building HTML failed.")


def latex():
    check_build()
    if sys.platform != 'win32':
        # LaTeX format.
        if os.system('sphinx-build -b latex -d build/doctrees '
                     '. build/latex'):
            raise SystemExit("Building LaTeX failed.")
        # Produce pdf.

        os.chdir('build/latex')

        # Call the makefile produced by sphinx...
        if os.system('make'):
            raise SystemExit("Rendering LaTeX failed.")

        os.chdir('../..')
    else:
        print('latex build has not been tested on windows')


def check_build():
    build_dirs = [
        'build', 'build/doctrees', 'build/html',
        'build/latex', 'build/plots', 'build/_static',
        'build/_templates']
    for d in build_dirs:
        try:
            os.mkdir(d)
        except OSError:
            pass


def all():
    # clean()
    html()


funcd = {
    'html': html,
    'latex': latex,
    'clean': clean,
    'all': all,
}

small_docs = False

if len(sys.argv)>1:
    if '--small' in sys.argv[1:]:
        small_docs = True
        sys.argv.remove('--small')
    for arg in sys.argv[1:]:
        func = funcd.get(arg)
        if func is None:
            raise SystemExit('Do not know how to handle %s; valid args are %s'%(
                    arg, funcd.keys()))
        func()
else:
    small_docs = False
    all()
# os.chdir(current_dir)
