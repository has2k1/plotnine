.. currentmodule:: ggplot
.. _api:

*************
API Reference
*************


Main
~~~~

.. autosummary::
   :toctree: generated/

   ggplot
   aes

Geoms, statistics and faceting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   geom_abline
   geom_area
   geom_bar
   geom_density
   geom_histogram
   geom_hline
   geom_jitter
   geom_line
   geom_now_its_art
   geom_point
   geom_step
   geom_text
   geom_tile
   geom_vline
   stat_bin2d
   stat_function
   stat_smooth
   facet_grid
   facet_wrap


Title, legends, labels
~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   ggtitle
   labs
   xlab
   xlim
   ylab
   ylim


Scales
~~~~~~

.. autosummary::
   :toctree: generated/

   scale_color_gradient
   scale_colour_gradient
   scale_colour_gradient2
   scale_colour_manual
   scale_facet_grid
   scale_facet_wrap
   scale_x_continuous
   scale_x_date
   scale_x_reverse
   scale_y_continuous
   scale_y_reverse
   
Themes
~~~~~~

.. autosummary::
   :toctree: generated/

   theme_bw
   theme_gray
   theme_matplotlib
   theme_xkcd

   
Rendering/ saving the plot
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/

   ggsave

Data sets
~~~~~~~~~

These data sets are included for documentation purpose and examples. They are loaded on demand.

.. csv-table::
   :header: "data set name","description"
   :delim: |

   ``diamonds`` | Prices of 50,000 round cut diamonds
   ``mtcars`` | Fuel consumption and 10 aspects of automobile design and performance for 32 automobiles (1973-74 models)
   ``meat`` | Livestock and Meat Domestic Data (1944-2012)
   ``pageviews`` | Page view data (2012-2013)
   
Internals
~~~~~~~~~

These are the base classes. 

.. autosummary::
   :toctree: generated/

   ggplot.geoms.geom
   ggplot.themes.theme
   ggplot.scales.scale


Some misc internal helper methods.

.. autosummary::
   :toctree: generated/

   date_breaks
   date_format
   draw_legend
   
#   colors
#   linestyles
#   shapes
#   size
#   scale_facet
#   scale_reverse

