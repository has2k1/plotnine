.. _index:

.. figure:: ./images/logo-540.png
   :alt: plotnine
   :align: right
   :scale: 33%
   :class: no-scaled-link

A Grammar of Graphics for Python
================================

plotnine is an implementation of a *grammar of graphics* in Python
based on ggplot2_. The grammar allows you to compose plots by explicitly
mapping variables in a dataframe to the visual objects that make up the plot.

Plotting with a *grammar of graphics* is powerful. Custom (and otherwise
complex) plots are easy to think about and build incremently, while
the simple plots remain simple to create.

Example
-------
.. code:: python

    from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap
    from plotnine.data import mtcars

    (ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
     + geom_point()
     + stat_smooth(method="lm")
     + facet_wrap("~gear"))

.. figure:: ./images/readme-image-4.png
   :scale: 33%
   :class: no-scaled-link

Documentation
-------------

.. toctree::
   :maxdepth: 1

   api
   installation
   gallery
   changelog
   about-plotnine
   tutorials
   glossary
   external-resources

.. _ggplot2: https://ggplot2.tidyverse.org
