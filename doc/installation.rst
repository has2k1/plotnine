Installation
============

plotnine can be can be installed in a couple of ways, depending on purpose.


Official release installation
-----------------------------
For a normal user, it is recommended to install the official release. You
can choose one these two commands:

.. code-block:: console

    # Using pip
    $ pip install plotnine         # 1. should be sufficient for most
    $ pip install 'plotnine[all]'  # 2. includes extra/optional packages

    # Or using conda
    $ conda install -c conda-forge plotnine

The second pip command also installs packages that are required for some
specific functionality that may not be frequently used. Those packages
are:

- `scikit-misc`_ - For loess smoothing
- `scikit-learn`_ - For Gaussian process smoothing

Development installation
------------------------
To do any development you have to clone the
`plotnine source repository`_ and install
the package in development mode. These commands do all of that:

.. code-block:: console

    $ git clone https://github.com/has2k1/plotnine.git
    $ cd plotnine
    $ pip install -e .

If you only want to use the latest development sources and do not
care about having a cloned repository, e.g. if a bug you care about
has been fixed but an official release has not come out yet, then
use this command:

.. code-block:: console

    $ pip install git+https://github.com/has2k1/plotnine.git

.. _plotnine source repository: https://github.com/has2k1/plotnine
.. _scikit-learn: http://scikit-learn.com
.. _scikit-misc: https://has2k1.github.io/scikit-misc/
