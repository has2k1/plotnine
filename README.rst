{ggplot}
========

::

    from ggplot import *

    ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point() + \
        geom_line(color='lightblue') + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")

What is it?
~~~~~~~~~~~

Yes, it's another implementation of
```ggplot2`` <https://github.com/hadley/ggplot2>`__. One of the biggest
reasons why I continue to reach for ``R`` instead of ``Python`` for data
analysis is the lack of an easy to use, high level plotting package like
``ggplot``. I've tried other libraries like ``Bockah`` and ``d3py`` but
what I really want is ``ggplot2``.

``ggplot`` is just that. It's an extremely un-pythonic package for doing
exactly what ``ggplot2`` does. The goal of the package is to mimic the
``ggplot2`` API. This makes it super easy for people coming over from
``R`` to use, and prevents you from having to re-learn how to plot
stuff.

Goals
~~~~~

-  same API as ``ggplot2`` for ``R``
-  tight integration with
   ```pandas`` <https://github.com/pydata/pandas>`__
-  pip installable

Getting Started
~~~~~~~~~~~~~~~

Dependencies
^^^^^^^^^^^^

-  ``matplotlib``
-  ``pandas``
-  ``numpy``
-  ``scipy``
-  ``statsmodels``

   unzip the matplotlibrc
   ======================

   $ unzip matplotlibrc.zip # install ggplot using pip $ pip install
   ggplot

Examples
~~~~~~~~

``geom_point``
^^^^^^^^^^^^^^

::

    from ggplot import *
    ggplot(diamonds, aes('carat', 'price')) + \
        geom_point(alpha=1/20.)

``geom_hist``
^^^^^^^^^^^^^

::

    p = ggplot(aes(x='carat'), data=diamonds)
    p + geom_hist() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq") 

``geom_bar``
^^^^^^^^^^^^

::

    p = ggplot(mtcars, aes('cyl'))
    p + geom_bar()

TODO
~~~~

-  finish README
-  add matplotlibrc to build script
-  distribute on PyPi (DONE)
-  come up with better name (DONE)
-  handle NAs gracefully (DONE)
-  make ``aes`` guess what the user actually means (DONE)
-  aes:

   -  size
   -  se for stat\_smooth (DONE)
   -  fix fill/colour (color DONE)

-  geoms:

   -  geom\_abline (DONE)
   -  geom\_area (DONE)
   -  geom\_bar (IN PROGRESS)
   -  geom\_boxplot
   -  geom\_hline (DONE)
   -  geom\_ribbon (same as geom\_ribbon?)
   -  geom\_vline (DONE)
   -  stat\_bin2d (DONE)
   -  geom\_jitter
   -  stat\_smooth (bug)

-  scales:

   -  scale\_colour\_brewer
   -  scale\_colour\_gradient
   -  scale\_colour\_gradient2
   -  scale\_x\_continuous
   -  scale\_x\_discrete
   -  scale\_y\_continuous

-  facets:

   -  facet\_grid (DONE)


