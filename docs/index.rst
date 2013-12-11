.. currentmodule:: ggplot
.. _index:

.. ipython:: python
   :suppress:

   import matplotlib.pyplot as plt
   plt.close('all')


ggplot from `Yhat <http://yhathq.com>`__
==========================================

read more on our
`blog <http://blog.yhathq.com/posts/ggplot-for-python.html>`__

.. ipython:: python

    from ggplot import *

    gg = ggplot(aes(x='date', y='beef'), data=meat) + \
        geom_point(color='lightblue') + \
        stat_smooth(span=.15, color='black', se=True) + \
        ggtitle("Beef: It's What's for Dinner") + \
        xlab("Date") + \
        ylab("Head of Cattle Slaughtered")
    @savefig index_example.png scale=75%
    print(gg)

What is it?
~~~~~~~~~~~

Yes, it's another port of
`ggplot2 <https://github.com/hadley/ggplot2>`__. One of the biggest
reasons why I continue to reach for ``R`` instead of ``Python`` for data
analysis is the lack of an easy to use, high level plotting package like
``ggplot2``. I've tried other libraries like
`bokeh <https://github.com/continuumio/bokeh>`__ and
`d3py <https://github.com/mikedewar/d3py>`__ but what I really want
is ``ggplot2``.

``ggplot`` is just that. It's an extremely un-pythonic package for doing
exactly what ``ggplot2`` does. The goal of the package is to mimic the
``ggplot2`` API. This makes it super easy for people coming over from
``R`` to use, and prevents you from having to re-learn how to plot
stuff.

Goals
~~~~~

-  same API as ``ggplot2`` for ``R``
-  never use matplotlib again
-  ability to use both American and British English spellings of
   aesthetics
-  tight integration with
   `pandas <https://github.com/pydata/pandas>`__
-  pip installable

Overview
========

.. toctree::
   :maxdepth: 2
   
   getting_started
   contributing
   todo
   api
