
.. _api:


#############
API Reference
#############

geoms
=====
.. currentmodule:: ggplot.geoms

.. autosummary::
   :toctree: generated/
   :nosignatures:
   :template: only-docstring.rst

   geom_abline
   geom_area
   geom_bar
   geom_blank
   geom_boxplot
   geom_crossbar
   geom_density
   geom_dotplot
   geom_errorbar
   geom_errorbarh
   geom_freqpoly
   geom_histogram
   geom_hline
   geom_jitter
   geom_label
   geom_line
   geom_linerange
   geom_path
   geom_point
   geom_pointrange
   geom_polygon
   geom_quantile
   geom_qq
   geom_rect
   geom_ribbon
   geom_rug
   geom_segment
   geom_smooth
   geom_spoke
   geom_step
   geom_text
   geom_tile
   geom_violin
   geom_vline


Related to geoms
----------------

.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   annotate
   arrow


Labels
------
.. currentmodule:: ggplot.labels

.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   labs
   xlab
   ylab
   ggtitle


stats
=====
.. currentmodule:: ggplot.stats

.. autosummary::
   :toctree: generated/
   :nosignatures:
   :template: only-docstring.rst

   stat_bin
   stat_bin_2d
   stat_bindot
   stat_boxplot
   stat_count
   stat_density
   stat_ecdf
   stat_function
   stat_identity
   stat_qq
   stat_quantile
   stat_smooth
   stat_sum
   stat_summary
   stat_summary_bin
   stat_unique
   stat_ydensity


facets
======
.. currentmodule:: ggplot.facets

.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   facet_grid
   facet_null
   facet_wrap
   ~labelling.labeller
   ~labelling.as_labeller
   ~labelling.label_value
   ~labelling.label_both
   ~labelling.label_context


scales
======
.. currentmodule:: ggplot.scales


Base scales
-----------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   ~scale.scale
   ~scale.scale_discrete
   ~scale.scale_continuous


Alpha scales
------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_alpha
   scale_alpha_discrete
   scale_alpha_continuous


Identity Scales
---------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_alpha_identity
   scale_color_identity
   scale_colour_identity
   scale_fill_identity
   scale_linetype_identity
   scale_shape_identity
   scale_size_identity


Color and fill scales
---------------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   ~scale.scale
   ~scale.scale_continuous

   scale_color_brewer
   scale_color_cmap
   scale_color_continuous
   scale_color_desaturate
   scale_color_discrete
   scale_color_distiller
   scale_color_gradient
   scale_color_gradient2
   scale_color_gradientn
   scale_color_gray
   scale_color_grey
   scale_color_hue
   scale_fill_brewer
   scale_fill_cmap
   scale_fill_continuous
   scale_fill_desaturate
   scale_fill_discrete
   scale_fill_distiller
   scale_fill_gradient
   scale_fill_gradient2
   scale_fill_gradientn
   scale_fill_gray
   scale_fill_grey
   scale_fill_hue


Manual scales
-------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_alpha_manual
   scale_color_manual
   scale_colour_manual
   scale_fill_manual
   scale_linetype_manual
   scale_shape_manual
   scale_size_manual


Linetype scales
---------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_linetype
   scale_linetype_discrete


Shape scales
------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_shape
   scale_shape_discrete


Size scales
-----------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_size
   scale_size_area
   scale_size_continuous
   scale_size_discrete
   scale_size_radius


Position scales
---------------
.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   scale_x_continuous
   scale_x_date
   scale_x_datetime
   scale_x_discrete
   scale_x_log10
   scale_x_reverse
   scale_x_sqrt
   scale_x_timedelta
   scale_y_continuous
   scale_y_date
   scale_y_datetime
   scale_y_discrete
   scale_y_log10
   scale_y_reverse
   scale_y_sqrt
   scale_y_timedelta


Scale limits
-------------
.. currentmodule:: ggplot.scales

.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   lims
   xlim
   ylim


positions
=========
.. currentmodule:: ggplot.positions

.. autosummary::
   :toctree: generated/
   :template: only-docstring.rst

   position_dodge
   position_fill
   position_identity
   position_jitter
   position_jitterdodge
   position_nudge
   position_stack
