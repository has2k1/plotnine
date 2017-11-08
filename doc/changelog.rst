Changelog
=========

v0.3.0
------
*(2017-11-08)*

API Changes
***********

- :class:`~plotnine.geoms.geom_smooth` gained an extra parameter
  ``legend_fill_ratio`` that control the area of the legend that is filled
  to indicate confidence intervals. (:issue:`32`)

- :meth:`plotnine.ggplot.save` gained an extra parameter ``verbose``.
  It no longer guesses when to print information and when not to.

- :meth:`plotnine.ggplot.draw` gained an extra parameter ``return_ggplot``.

- If the ``minor_breaks`` parameter of scales is a callable, it now
  expects one argument, the ``limits``. Previously it accepted
  ``breaks`` and ``limits``.

New Features
************

- Added :class:`~plotnine.animation.PlotnineAnimation` for animations.
- Added :class:`~plotnine.watermark.watermark` for watermarks.
- Added datetime scales for ``alpha``, ``colour``, ``fill`` and ``size``
  aesthetics

Enhancements
************

- Changed parameter settings for :class:`~plotnine.stats.stat_smooth`.

  #. Default ``span=0.75`` instead of ``2/3``
  #. When using loess smoothing, the control parameter ``surface``
     is only set to the value ``'direct'`` if predictions will
     be made outside the data range.


- Better control of scale limits. You can now specify individual limits of a scale.

  .. code-block:: python

     scale_y_continuous(limits=(0, None))
     xlim(None, 100)

  You can also use :func:`~plotnine.scales.expand_limits`

- Low and high :class:`~plotnine.scales.scale` limits can now be expanded
  separately with different factors multiplicative and additive factors.

- The layer parameter `show_legend` can now accept a ``dict`` for finer
  grained control of which aesthetics to exclude in the legend.

- Infinite values are removed before statistical computations ``stats``
  (:issue:`40`).

  ``stats`` also gained new parameter ``na_rm``, that controls whether
  missing values are removed before statistical computations.

- :func:`~plotnine.qplot` can now use the name and a Pandas series to
  label the scales of the aesthetics.

- You can now put stuff to add to a ggplot object into a list and add that
  that instead. No need to wrap the list around the internal class
  `Layers`.

  .. code-block:: python

     lst = [geom_point(), geom_line()]
     g = ggplot(df, aes('x', 'y'))
     print(g + lst)

  Using a list allows you to bundle up objects. I can be convenient when
  creating some complicated plots. See the Periodic Table Example.

Bug Fixes
*********

- Fixed bug where facetting led to a reordering of the data. This
  would manifest as a bug for ``geoms`` where order was important.
  (:issue:`26`)

- Fix bug where facetting by a column whose name (eg. ``class``) is
  a python keyword resulted in an exception. (:issue:`28`)

- Fix bug where y-axis scaling was calculated from the ``xlim`` argument.

- Fix bug where initialising geoms from stats, and positions from geoms,
  when passed as classes (e.g. ``stat_smooth(geom=geom_point)``, would
  fail.

- Fixed bug in :meth:`plotnine.ggplot.save` where specifying the ``width``
  and ``height`` would mess up the ``strip_text`` and ``spacing`` for the
  facetted plots. (:issue:`44`).

- Fixed bug in :class:`~plotnine.geoms.geom_abline`,
  :class:`~plotnine.geoms.geom_hline` and :class:`~plotnine.geoms.geom_vline`
  where facetting on a column that is not mapped to an aesthetic fails.
  (:issue:`48`)

- Fixed bug in :class:`~plotnine.geoms.geom_text`, the ``fontstyle`` parameter
  was being ignored.

- Fixed bug where boolean data was mapped to the same value on the coordinate
  axis. (:issue:`57`)

- Fixed bug in :class:`~plotnine.facets.facet_grid` where the ``scales``
  sometimes has no effect. (:issue:`58`)

- Fixed bug in :class:`~plotnine.stats.stat_boxplot` where setting the
  ``width`` parameter caused an exception.


v0.2.1
------
*(2017-06-22)*

- Fixed bug where manually setting the aesthetic ``fill=None`` or
  ``fill='None'`` could lead to a black fill instead of an empty
  fill.

- Fixed bug where computed aesthetics could not be used in larger
  statements. (:issue:`7`)

- Fixed bug in :class:`~plotnine.stats.stat_summary` where the you got
  an exception for some types of the `x` aesthetic values.

- Fixed bug where ``ggplot(data=df)`` resulted in an exception.

- Fixed missing axis ticks and labels for :class:`~plotnine.facets.facet_wrap`
  when the scales are allowed to vary (e.g `scales='free'`) between
  the panels.

- Fixed bug in :class:`~plotnine.stats.stat_density` where changing the
  x limits lead to an exception (:issue:`22`)


v0.2.0
------
*(2017-05-18)*

- Fixed bug in :class:`~plotnine.scales.scale_x_discrete` and
  :class:`~plotnine.scales.scale_y_discrete` where if they were
  instantiated with parameter ``limits`` that is either a numpy
  array or a pandas series, plotting would fail with a
  :class:`ValueError`.

- Fixed exceptions when using :func:`pandas.pivot_table` for Pandas v0.20.0.
  The API was `fixed <http://pandas.pydata.org/pandas-docs/version/0.20/whatsnew.html#pivot-table-always-returns-a-dataframe>`_.

- Fixed issues where lines/paths with segments that all belonged in the
  same group had joins that in some cases were "butted".


API Changes
***********

- :class:`~plotnine.geoms.geom_text` now uses ``ha`` and ``va`` as
  parameter names for the horizontal and vertical alignment. This
  is what matplotlib users expect. The previous names ``hjust`` and
  ``vjust`` are silently accepted.

- :func:`~plotnine.layer.Layers` can now be used to bundle up ``geoms``
  and ``stats``. This makes it easy to reuse ``geoms`` and `stats` or
  organise them in sensible bundles when making complex plots.

v0.1.0
------
*(2017-04-25)*

First public release
