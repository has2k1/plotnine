Changelog
=========

v0.2.1
------
*(unreleased)*

- Fixed bug where manually setting the aesthetic ``fill=None`` or
  ``fill='None'`` could lead to a black fill instead of an empty
  fill.


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
