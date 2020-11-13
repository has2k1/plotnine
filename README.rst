########
plotnine
########

=================    =================
Latest Release       |release|_
License              |license|_
DOI                  |doi|_
Build Status         |buildstatus|_
Coverage             |coverage|_
Documentation        |documentation|_
=================    =================

.. raw:: html

      <img src="https://github.com/has2k1/plotnine/blob/master/doc/images/logo-180.png" align="right"'>

plotnine is an implementation of a *grammar of graphics* in Python,
it is based on ggplot2_. The grammar allows users to compose plots
by explicitly mapping data to the visual objects that make up the
plot.

Plotting with a grammar is powerful, it makes custom (and otherwise
complex) plots easy to think about and then create, while the
simple plots remain simple.

To find out about all building blocks that you can use to create a
plot, check out the documentation_. Since plotnine has an API
similar to ggplot2, where we lack in coverage the
`ggplot2 documentation`_ may be of some help.

Example
-------

.. code:: python

    from plotnine import *
    from plotnine.data import mtcars

Building a complex plot piece by piece.

1. Scatter plot

   .. code:: python

       (ggplot(mtcars, aes('wt', 'mpg'))
        + geom_point())

   .. figure:: ./doc/images/readme-image-1.png

2. Scatter plot colored according some variable

   .. code:: python

       (ggplot(mtcars, aes('wt', 'mpg', color='factor(gear)'))
        + geom_point())

   .. figure:: ./doc/images/readme-image-2.png

3. Scatter plot colored according some variable and
   smoothed with a linear model with confidence intervals.

   .. code:: python

       (ggplot(mtcars, aes('wt', 'mpg', color='factor(gear)'))
        + geom_point()
        + stat_smooth(method='lm'))

   .. figure:: ./doc/images/readme-image-3.png

4. Scatter plot colored according some variable,
   smoothed with a linear model with confidence intervals and
   plotted on separate panels.

   .. code:: python

       (ggplot(mtcars, aes('wt', 'mpg', color='factor(gear)'))
        + geom_point()
        + stat_smooth(method='lm')
        + facet_wrap('~gear'))

   .. figure:: ./doc/images/readme-image-4.png

5. Make it playful

   .. code:: python

       (ggplot(mtcars, aes('wt', 'mpg', color='factor(gear)'))
        + geom_point()
        + stat_smooth(method='lm')
        + facet_wrap('~gear')
        + theme_xkcd())

   .. figure:: ./doc/images/readme-image-5.png


Installation
------------

Official release

.. code-block:: console

    # Using pip
    $ pip install plotnine         # 1. should be sufficient for most
    $ pip install 'plotnine[all]'  # 2. includes extra/optional packages

    # Or using conda
    $ conda install -c conda-forge plotnine


Development version

.. code-block:: console

    $ pip install git+https://github.com/has2k1/plotnine.git

Contributing
------------
Our documentation could use some examples, but we are looking for something
a little bit special. We have two criteria:

1. Simple looking plots that otherwise require a trick or two.
2. Plots that are part of a data analytic narrative. That is, they provide
   some form of clarity showing off the `geom`, `stat`, ... at their
   differential best.

If you come up with something that meets those criteria, we would love to
see it. See plotnine-examples_.

If you discover a bug checkout the issues_ if it has not been reported,
yet please file an issue.

And if you can fix a bug, your contribution is welcome.

.. |release| image:: https://img.shields.io/pypi/v/plotnine.svg
.. _release: https://pypi.python.org/pypi/plotnine

.. |license| image:: https://img.shields.io/pypi/l/plotnine.svg
.. _license: https://pypi.python.org/pypi/plotnine

.. |buildstatus| image:: https://github.com/has2k1/plotnine/workflows/build/badge.svg?branch=master
.. _buildstatus: https://github.com/has2k1/plotnine/actions?query=branch%3Amaster+workflow%3A%22build%22

.. |coverage| image:: https://codecov.io /github/has2k1/plotnine/coverage.svg?branch=master
.. _coverage: https://codecov.io/github/has2k1/plotnine?branch=master

.. |documentation| image:: https://readthedocs.org/projects/plotnine/badge/?version=latest
.. _documentation: https://plotnine.readthedocs.io/en/latest/

.. |doi| image:: https://zenodo.org/badge/89276692.svg
.. _doi: https://zenodo.org/badge/latestdoi/89276692

.. _ggplot2: https://github.com/tidyverse/ggplot2

.. _`ggplot2 documentation`: http://ggplot2.tidyverse.org/reference/index.html

.. _issues: https://github.com/has2k1/plotnine/issues

.. _plotnine-examples: https://github.com/has2k1/plotnine-examples
