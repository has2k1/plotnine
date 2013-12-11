.. currentmodule:: ggplot
.. _getting_started:

.. ipython:: python
   :suppress:

   import matplotlib.pyplot as plt
   plt.close('all')


Getting Started
~~~~~~~~~~~~~~~

Dependencies
^^^^^^^^^^^^

I realize that these are not fun to install. My best luck has always
been using ``brew`` if you're on a Mac or just using `the
binaries <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`__ if you're on
Windows. If you're using Linux then this should be relatively painless.
You should be able to ``apt-get`` or ``yum`` all of these. -
``matplotlib`` - ``pandas`` - ``numpy`` - ``scipy`` - ``statsmodels`` -
``patsy``

Installation
^^^^^^^^^^^^

Ok the hard part is over. Installing ``ggplot`` is really easy. Just use
``pip``!

::

    $ pip install ggplot

Loading ggplot
^^^^^^^^^^^^^^

.. ipython:: python

    from ggplot import *

That's it! You're ready to go!

Examples
~~~~~~~~

.. ipython:: python

    meat_lng = pd.melt(meat[['date', 'beef', 'pork', 'broilers']], id_vars='date')
    gg = ggplot(aes(x='date', y='value', colour='variable'), data=meat_lng) + \
        geom_point() + \
        stat_smooth(color='red')
    @savefig point_smooth.png scale=75%
    print(gg)

geom_point
^^^^^^^^^^^

.. ipython:: python

    from ggplot import *
    gg = ggplot(diamonds, aes('carat', 'price')) + \
        geom_point(alpha=1/20.) + \
        ylim(0, 20000)
    @savefig point.png scale=75%
    print(gg)

geom_histogram
^^^^^^^^^^^^^^

.. ipython:: python

    p = ggplot(aes(x='carat'), data=diamonds)
    gg = p + geom_histogram() + ggtitle("Histogram of Diamond Carats") + labs("Carats", "Freq")
    @savefig hist.png scale=75%
    print(gg)

geom_density
^^^^^^^^^^^^

.. ipython:: python

    gg = ggplot(diamonds, aes(x='price', color='cut')) + \
        geom_density()
    @savefig density.png scale=75%
    print(gg)

.. ipython:: python

    meat_lng = pd.melt(meat[['date', 'beef', 'broilers', 'pork']], id_vars=['date'])
    p = ggplot(aes(x='value', colour='variable', fill=True, alpha=0.3), data=meat_lng)
    gg = p + geom_density()
    @savefig density2.png scale=75%
    print(gg)

geom_bar
^^^^^^^^

.. ipython:: python

    p = ggplot(mtcars, aes('factor(cyl)'))
    gg = p + geom_bar()
    @savefig bar.png scale=75%
    print(gg)