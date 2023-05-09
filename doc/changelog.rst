.. _changelog:

Changelog
=========

v0.11.0
-------
(2023-05-09)

New Features
************

- A layout manager. Now you do not have to adjust spacing parameters
  to prevent objects around the panels from overlapping.
  Specifically, you can:

  1. Set the legend position to "top", "left" or "bottom"
  2. Use a large or multiline plot title
  3. Use a large or multiline plot caption
  4. Use :class:`~plotnine.facets.facet_wrap` with :py:`scales="free"`
     :py:`scales="free_x"` or :py:`scales="free_y"`

  You can now also align the `plot_title`, `axis_title_x`, `axis_title_y`
  and `plot_caption` with respect to the panels. Set these to "left",
  "right" & "center" for the horizontal flowing text. And "top", "right"
  & "center" for the vertical flowing text.

  Also, the size of the figure is exactly determined by the theme setting.
  For example, this:

  .. code-block:: python

     theme(figure_size=(8, 6), dpi=100)

  will create an `800px x 600px` image.

- You can create a ``subtitle`` using :class:`~plotnine.labels.labs` and
  style it using the ``plot_subtitle`` parameter to :class:`~plotnine.themes.theme`.

  .. code-block:: python

     theme(plot_subtitle=element_text(size=8))


Enhancements
************

- :class:`~plotnine.ggplot` object gained a new method
  :meth:`~plotnine.ggplot.save_helper`. It gives you access to the
  matplotlib figure that will be saved to file.

- When plotting with an ipython interactive backend (e.g. in a
  jupyter notebook). The default image output is retina. You
  do not need to run this command.

  .. code-block:: python

     %config InlineBackend.figure_format = "retina"

  Plotnine still respects any values set the user.

- In an interactive setting, after drawing an image. The size of the figure
  (in pixels) is printed e.g. `<Figure Size: (640 x 480)>`. Previously,
  something like `<ggplot: (336175301)>` was printed.

API Changes
***********

- :meth:`~plotnine.ggplot.__add__` and :meth:`~plotnine.ggplot.__iadd__`
  now accept the same types of objects. In this change
  :meth:`~plotnine.ggplot.__iadd__` has gained the ability to accept a
  list of objects.

- :meth:`~plotnine.ggplot.draw` no longer accepts the argument
  ``return_ggplot`` and the return value is always a matplolib figure.

- Themeables :meth:`~plotnine.themes.themeable.strip_margin`,
  :meth:`~plotnine.themes.themeable.strip_margin_x` and
  :meth:`~plotnine.themes.themeable.strip_margin_y` have been renamed to
  :meth:`~plotnine.themes.themeable.strip_align`,
  :meth:`~plotnine.themes.themeable.strip_align_x`
  :meth:`~plotnine.themes.themeable.strip_align_y` repectively.

- :meth:`~plotnine.themes.themeables.subplots_adjust` has been deprecated.
  You no longer need to use :py:`theme(subplots_adjust={"right": 0.85})` and
  the like to make space for the legend or text around the panels.
  In the future, this will through an error.

- Changed default font-family (san-serif) from DejaVu Sans to Helvetica.

Bug Fixes
*********

- Fixed bug where a discrete position scale failed when mapping
  an empty variable. (:issue:`647`)

- Fixed bug where :class:`~plotnine.facets.facet_grid` with a datetime
  column run into an exception. (:issue:`629`)

- Fixed bug where :class:`~plotnine.geoms.geom_violin` with facetting
  and `"scales = free"` did not work. (:issue:`655`)

- Fixed bug in :class:`~plotnine.positions.position_dodge2` to work with
  `preserve="single"` for :class:`~plotnine.geoms.geom_rect` and any other
  geoms that accept a min-max range along the x-axis.

- Fixed legend for :class:`~plotnine.geoms.geom_point` to accurately display
  transparent fill colors that have been manually set. (:issue:`665`)

- Fix issue where infinite limits for the `x` or `y` scales lead to an
  exception. (:issue:`664`)

- Fixed :class:`~plotnine.geoms.geom_text` and
  :class:`~plotnine.geoms.geom_label` when used with string formatting so that
  missing values are removed. (:issue:`651`)

v0.10.1
-------
(2022-09-10)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7124917.svg
   :target: https://doi.org/10.5281/zenodo.7124917

*This is a re-release of v0.10.0*.

In the previous release the project description fileformat changed
and not all references to it were corrected. PYPI read file that did
not exist, got no description. This release is fixes error.

v0.10.0
-------
(2022-09-10)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7124912.svg
   :target: https://doi.org/10.5281/zenodo.7124912

Bug Fixes
*********

- Fixed bug in :class:`~plotnine.stats.stat_bin_2d` where bins whose edges
  are zero or negative would yield the wrong plot. (:issue:`604`)

- Fixed bug :class:`~plotnine.stats.stat_density_2d` which had been broken
  by Matplotlib 1.6.0 (:issue:`619`)

- Fixed :class:`~plotnine.geoms.geom_text` when using ``adjust_text`` for
  the arrows to have the same color as the text.

New Features
************

- :class:`~plotnine.geoms.geom_ribbon` acquired new parameter ``where``
  which can be used shade withing given limits .

- Added support for objects with a ``to_pandas`` method to convert them to
  a pandas dataframe. You can now pass in `polars <https://pola.rs>`_ dataframes.

- :class:`~plotnine.geoms.geom_ribbon` acquired new parameter ``outline_type``
  which controls how to stroke the boundaries of the shaded area. This parameter
  is also available to :class:`~plotnine.geoms.geom_area` and
  :class:`~plotnine.geoms.geom_density`. :issue:`605`

API Changes
***********

- The automatic groups generated by the system and depending on the aesthetic
  mappings now only depend those aesthetics that have scales. This is more
  strict than has been, should affect very few cases of code that has been
  written and it should be less suprising to the users.

- :class:`~plotnine.geoms.geom_area` and :class:`~plotnine.geoms.geom_density`
  now default to showing only the upper outline/boundary of the area.
  Use ``outline_type="full"`` for the old behaviour.

v0.9.0
------
(2022-07-01)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7124918.svg
   :target: https://doi.org/10.5281/zenodo.7124918

API Changes
***********

- For the calls to ``ggplot``, the order of the positional arguments is
  ``(data, mapping)`` and for calls ``geoms`` and ``stats`` the order
  is ``(mapping, data)``. In practice, you can still provide one/two
  positional arguments in any order. However, the are a few cases
  where old code will breaks due to duplicate parameters.

New Features
************

- Added :class:`~plotnine.geoms.geom_pointdensity`, a 2D density plot
  that does not hide the distribution of the individual data points.

- :class:`~plotnine.positions.position_dodge2` gained the ability to reverse
  the order of the plotted groups. (:issue:`515`)

- Added :class:`~plotnine.themes.theme_tufte`, a theme that reduces the
  distractions around plot data.

- :class:`~plotnine.labels.labs` can now be used to create a ``caption``.
  This caption can be styled using the ``plot_caption`` parameter to
  :class:`~plotnine.themes.theme`.

  .. code-block:: python

      theme(plot_caption=element_text(size=13))

- You can now align the ``plot_title`` horizontally to the left or right.

  .. code-block:: python

      theme(plot_title=element_text(ha='left'))

  Before, the title was always centered.


Bug Fixes
*********

- Fixed bug in :class:`~plotnine.facets.facet_grid` and
  :class:`~plotnine.facets.facet_wrap` where the ``drop`` parameter was
  ignored. (:issue:`510`)

- Fixed issue with :class:`~plotnine.geoms.annotation_logticks` where the
  wrong range was used for the x|y axis. (:issue:`525`)

- Fixed bug in :class:`~plotnine.geoms.geom_smooth` where using a
  coordinate transformation without computing the standard error
  led to a crash. (:issue:`526`)

- Fixed bug where you could not specific the cap/end of a dashed line
  when styling a plot with :class:`~plotnine.themes.element_line`.

- Fixed legend for :class:`~plotnine.geoms.geom_map` so that the entries
  have the same stroke and points on the map. (:issue:`534`)

- Fixed :class:`~plotnine.geoms.geom_history` for some cases when it fails
  to automatically determine the number of bins. (:issue:`543`)

- Fixed :class:`~plotnine.facets.facet_grid` and
  :class:`~plotnine.facets.facet_wrap` when mapping to lists/arrays/series
  so that the rows mapped this way are not mixed up. (:issue:`548`)

- Fixed :class:`~plotnine.stats.stat_bin_2d` not to error for
  matplotlib >= 3.5.0 so that it does not throw a Numpy error.
  (:issue:`567`)

- Fixed :class:`~plotnine.geoms.geom_map` to be able to draw Polygons
  with holes in them.

- Fixed :class:`~plotnine.geoms.geom_map` to be able to draw MultiPolygons.

- Fixed :class:`~plotnine.scales.scale_x_discrete` and
  :class:`~plotnine.scales.scale_x_discrete` to work properly with ``None``
  values. (:issue:`523`)

- Fixed :class:`~plotnine.geoms.geom_point` to respect not to use the ``fill``
  mapping on unfilled shapes. (:issue:`100`)

- Fixed :class:`~plotnine.positions.position_stack` to work with scales that
  have non-linear transformations. e.g.
  :class:`~plotnine.scales.scale_y_log10`. (:issue:`580`)

- Fixed scales to work with limits passed as a function.

- Fixed :class:`~plotnine.themes.themeables.axis_ticks` so you can change
  the colour of the axis ticks. This was probably a regression due to changes
  in Matplotlib.

- Fixed :class:`~plotnine.themes.themeables.panel_ontop` so that if is set to
  ``False``, then the data visualised below the grid-lines. (:issue:`585`)

- Fixed :class:`~plotnine.geoms.geom_ribbon`, :class:`~plotnine.geoms.geom_area`
  and :class:`~plotnine.geoms.geom_density` to work with
  :class:`~plotnine.coords.coord_flip`. (:issue:`596`)

Enhancements
************

- :class:`~plotnine.stats.stat_summary` now has a default summary
  function. (:issue:`528`)

- :class:`~plotnine.stats.stat_density` now uses a fast computation path
  for gaussian densities with no weights. This was probably a regression.

- :class:`~plotnine.geoms.geom_map` can now draw MultiPoints,
  MultiLineStrings and MultiPolgons.

- :class:`~plotnine.geoms.geom_text` with ``adjust_text`` can now be used
  in more than one layer with good enough results.

v0.8.0
------
(2021-03-24)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4636791.svg
   :target: https://doi.org/10.5281/zenodo.4636791


API Changes
***********

- How you map to calculated aesthetics has changed. Use the
  :func:`~plotnine.mapping.evaluation.after_stat` function. The old
  methods ``'stat(name)'`` and ``'..name..'`` have been deprecated.

New Features
************

- You can now map to aesthetics at three different stages. See
  :class:`~plotnine.aes.aes`, :func:`~plotnine.aes.after_stat`,
  :func:`~plotnine.aes.after_scale` and :class:`~plotnine.aes.stage`.

- :class:`~plotnine.geoms.geom_violin` gained the a new parameter ``style``
  with which you can draw half violin (density curve on one side and flat
  on the other).

- Added :class:`~plotnine.geoms.geom_raster`.

- ``geoms`` gained new parameter ``raster`` for the
  :class:`~plotnine.layer.Layer`. You can use it to rasterize any layer
  when the resulting plot is of vector format e.g. ``pdf``.

- Using the ``space`` parameter, :class:`~plotnine.facets.facet_grid`
  gained the ability to have rows and columns of panels of different
  sizes.

Bug Fixes
*********

- Fixed issue where some plots with a colorbar would fail for specific
  themes. (:issue:`424`)

- Fixed :class:`~plotnine.geoms.geom_map` to plot ``MultiLineString`` geom types.

- Fixed :class:`~plotnine.geoms.geom_text` to allow any order of ``mapping`` and
  ``data`` positional arguments.

- Fixed bug were the plotted image may have ignored theming that relied on
  some Matplotlib rcParams. (:issue:`451`)

- Fixed the ``weight`` aesthetic in :class:`~plotnine.geoms.geom_boxplot`, previously
  ignored it is now recognised. (:issue:`438`)

- Fixed :class:`~plotnine.geoms.annotation_logticks` and
  :class:`~plotnine.geoms.annotation_stripes` to work without global data and
  aesthetics. (:issue:`469`)

- Fix :class:`~plotnine.scales.scale_shape_discrete` when print many unfilled shapes
  not to assign the same shapes to more than one group. (:issue:`473`)

- Fixed bug in :class:`~plotnine.stats.stat_ellipse` where the center of the ellipse
  assuming a multivariate t-distribution was incorrectly calculated. (:issue:`493`)

- Fixed calculation of ``ndensity`` in :class:`~plotnine.stats.stat_bin`.
  (:issue:`494`)


Enhancements
************
- Manual scales now match the values of the breaks if the breaks are given.
  (:issue:`445`)

- Using ``print`` to show a ggplot object will not show the hash
  (``<ggplot: ...>``) anymore. There is now a difference between
  ``repr(p)`` and ``str(p)``. (:issue:`453`)

- Added option to for the ``base_family`` of a theme, now you can set it
  once with and have it be applied to all themes. (:issue:`436`)

  .. code-block:: python

      from plotnine.options import set_option
      set_option('base_family', 'Comic Sans MS')

- You can now add ``None`` to a ggplot, doing so returns a copy of the
  the ggplot object. (:issue:`474`)

- Better handling of multiline facet labels. (:issue:`484`)

v0.7.1
------
(2020-08-05)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3973626.svg
   :target: https://doi.org/10.5281/zenodo.3973626

Bug Fixes
*********

- Fixed issue where a plot has no data and the geoms have no data,
  but the mappings are valid. (:issue:`404`)

- Fixed ``preserve='single'`` in :class:`plotnine.positions.position_dodge`
  and :class:`plotnine.positions.position_dodge2` to work for geoms that
  only have ``x`` aesthetic and not ``xmin`` and ``xmax``
  e.g :class:`plotnine.geoms.geom_text`.

- Fix regression in ``v0.7.0`` where plots with a colorbar
  would fail if using :class:`~plotnine.themse.theme_matplotlib`.

v0.7.0
------
(2020-06-05)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3878645.svg
   :target: https://doi.org/10.5281/zenodo.3878645


API Changes
***********

- Changed the default method of caculating bandwidth for all stats that
  use kernel density estimation. The affected stats are
  :class:`~plotnine.stats.stat_density`,
  :class:`~plotnine.stats.stat_ydensity`, and
  :class:`~plotnine.stats.stat_sina`. These stats can now work with groups
  that have a single unique value.

- Changed :class:`plotnine.scale.scale_colour_continuous` to refer to the same
  scale as :class:`plotnine.scale.scale_color_continuous`.

- Changed :class:`plotnine.scale.scale_color_cmap` so the parameter
  `cmap_name` refers to the name of the color palette and `name` refers
  to the name of the scale. (:issue:`371`)

New Features
************

- :class:`~plotnine.aes.aes` got an internal function ``reorder`` which
  makes it easy to change the ordering of a discrete variable according
  to some other variable/column.

- :class:`~plotnine.stats.stat_smooth` can now use formulae for linear
  models.


Bug Fixes
*********

- Fixed issue where a wrong warning could be issued about changing the
  transform of a specialised scale. It mostly affected the *timedelta*
  scale.

- Fixed :class:`plotnine.geoms.geom_violin` and other geoms when used
  with ``position='dodge'`` not to crash when if a layer has an empty
  group of data.

- Fixed bug in :class:`plotnine.geoms.geom_path` for some cases when groups
  had less than 2 points. (:issue:`319`)

- Fixed all stats that compute kernel density estimates to work when all
  the data points are the same. (:issue:`317`)

- Fixed issue where setting the group to a string value i.e. ``group='string'``
  outside ``aes()`` failed due to an error.

- Fixed issue where discrete position scales could not deal with fewer limits
  than those present in the data. (:issue:`342`)

- Fixed issue with using custom tuple linetypes~ with
  :class:`plotnine.scales.scale_linetype_manual`. (:issue:`352`)

- Fixed :class:`plotnine.geoms.geom_map` to work with facets. (:issue:`359`)

- Fixed :class:`plotnine.position.jitter_dodge` to work when ``color`` is
  used as an aesthetic. (:issue:`372`)

- Fixed :class:`plotnine.geoms.geom_qq` to work with facets (:issue:`379`)

- Fixed skewed head in :class:`plotnine.geoms.arrow` when drawn on
  facetted plot (:issue:`388`)

- Fixed issue with :class:`plotnine.stats.stat_density` where weights could
  not be used with a gaussian model. (:issue:`392`)

- Fixed bug where :class:`~plotnine.guides.guide_colorbar` width and height
  could not be controlled by
  :class:`~plotnine.themes.theamables.legend_key_width` and
  :class:`~plotnine.themes.theamables.legend_key_height`. (:issue:`360`)

Enhancements
************

- You can now set the bandwidth parameter ``bw`` of
  :class:`~plotnine.stats.stat_ydensity`.

- Parameters `ha` and `va` of :class:`~plotnine.geoms.geom_text` have been converted
  to aesthetics. You can now map to them. (:issue:`325`)

- All themes (except `theme_matplotlib`) now do not show minor ticks. (:issue:`348`)

v0.6.0
------
(2019-08-21)

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3373970.svg
   :target: https://doi.org/10.5281/zenodo.3373970

API Changes
***********

- The ``draw`` parameter of :class:`plotnine.geoms.geom_map` has been removed.
  Shapefiles should contain only one type of geometry and that is the geometry
  that is drawn.

- Ordinal (Ordered categorical) columns are now mapped to ordinal scales. This
  creates different plots.

- The default mapping for the computed aesthetic *size* of
  :class:`~plotnine.stat.stat_sum` has changed to ``'stat(n)'``. This also
  changes the default plot for :class:`~plotnine.geom.geom_count`.

New Features
************

- :class:`~plotnine.geoms.geom_text` gained the ``adjust_text`` parameter,
  and can now repel text.
- Added :class:`~plotnine.annotate.annotation_logticks`.
- Added :class:`~plotnine.geoms.geom_sina`
- Added scales for ordinal (ordered categorical) columns.
- :class:`~plotnine.geoms.geom_step` gained the option ``mid`` for the
  direction parameter. The steps are taken mid-way between adjacent x values.
- Added :class:`~plotnine.annotate.annotation_stripes`.

Bug Fixes
*********

- Fixed bug where facetting would fail if done on a plot with annotation(s)
  and one of the facetting columns was also a variable in the environment.

- Fixed bug where :class:`~plotnine.coords.coord_flip` would not flip
  geoms created by :class:`~plotnine.geoms.geom_rug` (:issue:`216`).

- Fixed bug where plots with :class:`~plotnine.themes.theme_xkcd` cannot be
  saved twice (:issue:`199`)

- Fixed bug that made it impossible to map to columns with the same name as
  a calculated columns of the stat. (:issue:`234`)

- Fixed bug in :class:`~plotnine.geoms.geom_smooth` that made it difficult
  to use it with stats other than :class:`~plotnine.stats.stat_smooth`.
  (:issue:`242`)

- Fixed bug in :class:`~plotnine.postions.position_dodge` where by bar plot
  could get thinner when facetting and useing ``preserve = 'single'``.
  (:issue:`224`)

- Fixed bug in :class:`~plotnine.coord.coord_trans` where if the transformation
  reversed the original limits, the order in which the data was laid out remained
  unchanged. (:issue:`253`)

- Fixed bug in :class:`~plotnine.stats.stat_count` where ``float`` weights were
  rounded and lead to a wrong plot. (:issue:`260`)

- Fixed bug where one could not use the British spelling ``colour`` to rename
  a color scale. (:issue:`264`)

- Fixed bug in :class:`~plotnine.scales.lims`, :class:`~plotnine.scales.xlim`,
  and :class:`~plotnine.scales.ylim` where ``datetime`` and ``timedelta`` limits
  resulted in an error.

- Fixed bug where :class:`~plotnine.geoms.geom_rect` could not be used with
  :class:`~plotnine.coord.coord_trans`. (:issue:`256`)

- Fixed bug where using free scales with facetting and flipping the coordinate
  axes could give unexpected results. (:issue:`286`)

- Fixed unwanted tick along the axis for versions of Matplotlib >= 3.1.0.

- Fixed :class:`~plotnine.geoms.geom_text` not to error when using ``hjust``
  and ``vjust``. (:issue:`287`)

- Fixed bug where :class:`~plotnine.geoms.geom_abline`
  :class:`~plotnine.geoms.geom_hline` and :class:`~plotnine.geoms.geom_vline`
  could give wrong results when used with :class:`~plotnine.coord.coord_trans`.

- Fixed bug where layers with only infinite values would lead to an exception
  if they were the first layer encountered when choosing a scale.

Enhancements
************

- Legends are now plotted in a predictable order which dedends on how the plot
  is constructed.

- The spokes drawn by :class:`~plotnine.geoms.geom_spoke` can now have a fixed
  angle.

- Aesthetics that share a scale (e.g. color and fill can have the same scale) get
  different guides if mapped to different columns.

- When the transform of a specialised (one that is not and identity scale) continuous
  scale is altered, the user is warned about a possible error in what they expect.
  (:issue:`254`, :issue:`255`)

- The ``method_args`` parameter in :class:`~plotnine.stats.stat_smooth` can now
  differentiate between arguments for initialising and those for fitting the
  smoothing model.

- :class:`~plotnine.postions.position_nudge` can now deal with more geoms e.g.
  :class:`~plotnine.geoms.geom_boxplot`.

- The ``limits`` parameter of :class:`~plotnine.scales.scale_x_discrete` and
    :class:`~plotnine.scales.scale_y_discrete` can now be a function.

- The ``width`` of the boxplot can now be set irrespective of the stat.

- The mid-point color of :class:`~plotnine.scales.scale_color_distiller` now
  matches that of the trainned data.

- The way in which layers are created has been refactored to give packages that
  that extend plotnine more flexibility in manipulating the layers.

- You can now specify one sided limits for coordinates. e.g.
  `coord_cartesian(limits=(None, 10))`.

- All the themeables have been lifted into the definition of
  :class:`~plotnine.themes.theme` so they can be suggested autocomplete.

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

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1464204.svg
   :target: https://doi.org/10.5281/zenodo.1464204

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

  Using a list allows you to bundle up objects. It can be convenient when
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
