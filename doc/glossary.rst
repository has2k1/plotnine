.. currentmodule:: plotnine

.. _glossary:

Glossary of Common Terms
========================

.. glossary::

    stat
        A subclass of :class:`~plotnine.stats.stat.stat`.

    geom
        A subclass of :class:`~plotnine.geoms.geom.geom`.

    position
        A subclass of :class:`~plotnine.positions.position.position`.

    expression
        A python expression wrapped in a string. The expression can
        refer to variables in the user environment and columns in
        the dataframe.

        The following may be valid expressions::

            'col1'
            'col1 + col2'
            'np.sin(col1)'
            '"string-value"'

