Changelog
=========

v0.5.2
------
(not-yet-released)

API Changes
***********

- The ``draw`` parameter of :class:`plotnine.geoms.geom_map` has been removed.
  Shapefiles should contain only one type of geometry and that is the geometry
  that is drawn.

Bug Fixes
*********

- Fixed bug where facetting would fail if done on a plot with annotation(s)
  and one of the facetting columns was also a variable in the environment.

v0.5.1
------
(2018-10-17)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1464803.svg
   :target: https://doi.org/10.5281/zenodo.1464803

Bug Fixes
*********

- Changed the dependency for mizani to ``v0.5.2``. This fixes an issue
  where facetting may create plots with missing items. (:issue:`210`)

v0.5.0
------
(2018-10-16)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.89276692.svg
   :target: https://doi.org/10.5281/zenodo.89276692

API Changes
***********

- Plotnine 0.5.0 only supports Python 3.5 and higher
- geopandas has been removed as a requirement for installation. Users of
  :class:`~plotnine.geoms.geom_map` will have to install it separately.
  (:issue:`178`)

Bug Fixes
*********

- Fixed issue where with the `subplots_adjust` themeable could not be used to
  set the `wspace` and `hspace` Matplotlib subplot parameters. (:issue:`185`)

- Fixed in :class:`~plotnine.stat.stat_bin` where setting custom limits for the
  scale leads to an error. (:issue:`189`)

- Fixed issue interactive plots where the x & y coordinates of the mouse do not
  show. (:issue:`187`)

- Fixed bug in :class:`~plotnine.geoms.geom_abline` where passing the mapping as
  a keyword parameter lead to a wrong plot. (:issue:`196`)

- Fixed issue where ``minor_breaks`` for tranformed scaled would have to be given
  in the transformed coordinates. Know they are given the data coordinates just
  like the major ``breaks``.

Enhancements
************

- For all geoms, with :class:`~plotnine.coords.coord_cartesian` ``float('inf')``
  or ``np.inf`` are interpreted as the boundary of the plot panel.

- Discrete scales now show missing data (``None`` and ``nan``). This behaviour
  is controlled by the new ``na_translate`` option.

- The ``minor_breaks`` parameter for continuous scales can now be given as an
  integer. An integer is taken to controll the number of minor breaks between
  any set of major breaks.

v0.4.0
------
*2018-01-08*

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1325309.svg
   :target: https://doi.org/10.5281/zenodo.1325309

API Changes
***********

- Calculated aesthetics are accessed using the :func:`~plotnine.aes.stat`
  function. The old method (double dots ``..name..``) still works.

- :class:`~plotnine.stats.stat_qq` calculates slightly different points
  for the theoretical quantiles.

- The ``scales`` (when set to *free*, *free_x* or *free_y*') parameter of
  :class:`~plotnine.facets.facet_grid` and :class:`~plotnine.facets.facet_wrap`
  assigns the same scale across the rows and columns.


New Features
************

- Added :class:`~plotnine.geoms.geom_qq_line` and
  :class:`~plotnine.stats.stat_qq_line`, for lines through Q-Q plots.

- Added :class:`~plotnine.geoms.geom_density_2d` and
  :class:`~plotnine.geoms.geom_stat_2d`.

- Added :class:`~plotnine.stats.stat_ellipse`.

- Added :class:`~plotnine.geom.geom_map`.

- Plotnine learned to respect plydata groups.

- Added :class:`~plotnine.stats.stat_hull`.

- Added :meth:`~plotnine.ggplot.save_as_pdf_pages`.

Bug Fixes
*********

- Fixed issue where colorbars may chop off the colors at the limits
  of a scale.

- Fixed issue with creating fixed mappings to datetime and timedelta
  type values.(:issue:`88`)

- Fixed :class:`~plotnine.scales.scale_x_datetime` and
  :class:`~plotnine.scales.scale_y_datetime` to handle the intercepts
  along the axes (:issue:`97`).

- Fixed :class:`~plotnine.stats.stat_bin` and
  :class:`~plotnine.stats.stat_bin_2d` to properly handle the
  ``breaks`` parameter when used with a transforming scale.

- Fixed issue with x and y scales where the ``name`` of the scale was
  ignored when determining the axis titles. Now, the ``name`` parameter
  is specified, it is used as the title. (:issue:`105`)

- Fixed bug in discrete scales where a column could not be mapped
  to integer values. (:issue:`108`)

- Make it possible to hide the legend with ``theme(legend_position='none')``.
  (:issue:`119`)

- Fixed issue in :class:`~plotnine.stats.stat_summary_bin` where some input
  values gave an error. (:issue:`123`)

- Fixed :class:`~plotnine.geoms.geom_ribbon` to sort data before plotting.
  (:issue:`127`)

- Fixed ``IndexError`` in :class:`~plotnine.facets.facet_grid` when row/column
  variable has 1 unique value. (:issue:`129`)

- Fixed :class:`~plotnine.facets.facet_grid` when ``scale='free'``,
  ``scale='free_x'`` or ``scale='free_y'``, the panels share axes
  along the row or column.

- Fixed :class:`~plotnine.geoms.geom_boxplot` so that user can create a boxplot
  by specifying all required aesthetics. (:issue:`136`)

- Fixed :class:`~plotnine.geoms.geom_violin` to work when some groups are empty.
  (:issue:`131`)

- Fixed continuous scales to accept ``minor=None`` (:issue:`120`)

- Fixed bug for discrete position scales, where ``drop=False`` did not drop
  unused categories (:issue:`139`)

- Fixed bug in :class:`~plotnine.stats.stat_ydensity` that caused an exception
  when a panel had no data. (:issue:`147`)

- Fixed bug in :class:`~plotnine.coords.coord_trans` where coordinate
  transformation and facetting could fail with a ``KeyError``. (:issue:`151`)

- Fixed bug that lead to a ``TypeError`` when aesthetic mappings to could be
  recognised as being groupable. It was easy to stumble on this bug when using
  :class:`~plotnine.geoms.geom_density`. (:issue:`165`)

- Fixed bug in :class:`~plotnine.facets.facet_wrap` where some combination of
  parameters lead to unexpected panel arrangements. (:issue:`163`)

- Fixed bug where the legend text of colorbars could not be themed. (:issue:`171`)

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

- You can now use a ``dict`` (with manual scales) to map data values to
  aesthetics (:issue:`169`).

- You can now specify infinite coordinates with :class:`plotnine.geoms.geom_rect`
  (:issue:`166`)

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
