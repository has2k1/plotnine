About plotnine
==============

History and objective
---------------------

plotnine started as an effort to improve the scaling functionality in
ggpy_ formally known as "ggplot for python". It was part of a larger
goal to evolve the package into one that supported a full plotting
grammar. It turned out that to have a *grammar of graphics* system we
had to just about start anew.

The complete guide to what constitutes a "Grammar of Graphics" is
Leland Wilkinson's book *The Grammar of Graphics*. To create ggplot2_
Hadley Wickham came up with an interpretation termed *A layered grammar
of graphics* [1]_. Core to the interpretation is a crucial plot building
pipeline [2]_ in ggplot2 that we adopted [3]_ for plotnine.

The R programming language has a rich statistical ecosystem that
ggplot2 taps into with ease. In plotnine we have done our best to
integrate with the rest of the scientific python ecosystem. Though we
feel we could do more on that integration, notwithstanding language
differences, users familiar with ggplot2 should be comfortable
and productive with plotnine.

Built with
----------
- matplotlib_ -  Plotting backend.
- pandas_ - Data handling.
- mizani_ - Scales framework.
- statsmodels_ - For various statistical computations.
- scipy_ -  For various statistical computation procedures.


.. [1] *The Grammar of Graphics* has to be interpreted into a form that
   can be implemented. We were not up to this task.

.. [2] This is more or less an implementation of what is depicted in
   *Figure 2.2* of *The Grammar of Graphics*

.. [3] By adopting a similar pipeline and user API as ``ggplot2`` the
   other internals referenced within the pipeline look similar.

.. _statsmodels: http://www.statsmodels.org
.. _pandas: http://pandas.pydata.org
.. _matplotlib: http://matplotlib.org
.. _scipy: https://scipy.org
.. _mizani: https://mizani.readthedocs.io
.. _ggplot2: http://ggplot2.org
.. _ggpy: https://github.com/yhat/ggpy`
