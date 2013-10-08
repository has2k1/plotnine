{ggplot}
========

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

::

    # unzip the matplotlibrc
    $ unzip matplotlibrc.zip ~/
    $ pip install ggplot

Examples
~~~~~~~~

TODO
~~~~

-  finish README
-  add matplotlibrc to build script
-  distribute on PyPi
-  come up with better name
-  handle NAs gracefully
-  make ``aes`` guess what the user actually means (DONE)
-  aes:

   -  size
   -  se for stat\_smooth
   -  fix fill/colour

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


