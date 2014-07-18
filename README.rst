|image|

{ggplot} from `Yhat <http://yhathq.com>`__
==========================================

read more on our
`blog <http://blog.yhathq.com/posts/ggplot-for-python.html>`__

::

    from ggplot import *

    ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/ggplot_demo_beef.png
   :alt: image

   image
What is it?
-----------

Yes, it's another port of
`ggplot2 <https://github.com/hadley/ggplot2>`__. One of the biggest
reasons why I continue to reach for ``R`` instead of ``Python`` for data
analysis is the lack of an easy to use, high level plotting package like
``ggplot2``. I've tried other libraries like
`bokeh <https://github.com/continuumio/bokeh>`__ and
`d3py <https://github.com/mikedewar/d3py>`__ but what I really want is
``ggplot2``.

``ggplot`` is just that. It's an extremely un-pythonic package for doing
exactly what ``ggplot2`` does. The goal of the package is to mimic the
``ggplot2`` API. This makes it super easy for people coming over from
``R`` to use, and prevents you from having to re-learn how to plot
stuff.

Goals
-----

-  same API as ``ggplot2`` for ``R``
-  ability to use both American and British English spellings of
   aesthetics
-  tight integration with `pandas <https://github.com/pydata/pandas>`__
-  pip installable

Getting Started
---------------

Dependencies
~~~~~~~~~~~~

This package depends on the following packages, although they should be
automatically installed if you use ``pip``:

-  ``matplotlib``
-  ``pandas``
-  ``numpy``
-  ``scipy``
-  ``statsmodels``
-  ``patsy``

Installation
~~~~~~~~~~~~

Installing ``ggplot`` is really easy. Just use ``pip``!

::

    $ pip install ggplot

Loading ``ggplot``
~~~~~~~~~~~~~~~~~~

::

    # run an IPython shell (or don't)
    $ ipython
    In [1]: from ggplot import *

That's it! You're ready to go!

Examples
--------

::

    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
        geom_point() + \
        stat_smooth(color='red')

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/ggplot_meat.png
   :alt: image

   image
``geom_point``
~~~~~~~~~~~~~~

::

    from ggplot import *
    ggplot(diamonds, aes('carat', 'price')) + \
        geom_point(alpha=1/20.) + \
        ylim(0, 20000)

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/diamonds_geom_point_alpha.png
   :alt: image

   image
``geom_histogram``
~~~~~~~~~~~~~~~~~~

::

    p = ggplot(aes(x='carat'), data=diamonds)
    p + geom_histogram() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq")

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/diamonds_carat_hist.png
   :alt: image

   image
``geom_density``
~~~~~~~~~~~~~~~~

::

    ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density()

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/geom_density_example.png
   :alt: image

   image
::

    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    p = ggplot(aes(x='value', colour='variable', fill=True, alpha=0.3), data=meat_lng)
    p + geom_density()

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/density_with_fill.png
   :alt: image

   image
``geom_bar``
~~~~~~~~~~~~

::

    p = ggplot(mtcars, aes('factor(cyl)'))
    p + geom_bar()

.. figure:: https://raw.github.com/yhat/ggplot/master/ggplot/tests/baseline_images/test_readme_examples/mtcars_geom_bar_cyl.png
   :alt: image

   image
TODO
----

`The list is long, but
distinguished. <https://github.com/yhat/ggplot/blob/master/TODO.md>`__
We're looking for contributors! Email greg at yhathq.com for more info.
For getting started with contributing, check out `these
docs <https://github.com/yhat/ggplot/blob/master/docs/contributing.rst>`__

|image|

.. |image| image:: https://secure.travis-ci.org/yhat/ggplot.png?branch=master
   :target: http://travis-ci.org/yhat/ggplot
.. |image| image:: https://ga-beacon.appspot.com/UA-46996803-1/ggplot/README.md
   :target: https://github.com/yhat/ggplot
