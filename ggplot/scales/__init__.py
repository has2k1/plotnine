from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# color
from .scale_color import scale_color_brewer, scale_colour_brewer
from .scale_color import scale_color_distiller, scale_colour_distiller
from .scale_color import scale_color_gradient, scale_colour_gradient
from .scale_color import scale_color_gradient2, scale_colour_gradient2
from .scale_color import scale_color_gradientn, scale_colour_gradientn
from .scale_color import scale_color_grey, scale_colour_grey
from .scale_color import scale_color_hue, scale_colour_hue
from .scale_color import scale_color_discrete, scale_colour_discrete
from .scale_color import scale_color_continuous, scale_colour_continuous
# fill
from .scale_color import scale_fill_discrete, scale_fill_continuous
from .scale_color import scale_fill_brewer
from .scale_color import scale_fill_distiller
from .scale_color import scale_fill_gradient
from .scale_color import scale_fill_gradient2
from .scale_color import scale_fill_gradientn
from .scale_color import scale_fill_grey
from .scale_color import scale_fill_hue
from .scale_color import scale_fill_discrete
from .scale_color import scale_fill_continuous
# alpha
from .scale_alpha import scale_alpha
from .scale_alpha import scale_alpha_discrete
from .scale_alpha import scale_alpha_continuous
# linetype
from .scale_linetype import scale_linetype
from .scale_linetype import scale_linetype_discrete
from .scale_linetype import scale_linetype_continuous
# shape
from .scale_shape import scale_shape
from .scale_shape import scale_shape_discrete
from .scale_shape import scale_shape_continuous
# size
from .scale_size import scale_size
from .scale_size import scale_size_discrete
from .scale_size import scale_size_continuous
# identity
from .scale_identity import scale_color_identity, scale_colour_identity
from .scale_identity import scale_fill_identity
from .scale_identity import scale_shape_identity
from .scale_identity import scale_linetype_identity
from .scale_identity import scale_alpha_identity
from .scale_identity import scale_size_identity
# manual
from .scale_manual import scale_color_manual, scale_colour_manual
from .scale_manual import scale_fill_manual
from .scale_manual import scale_shape_manual
from .scale_manual import scale_linetype_manual
from .scale_manual import scale_alpha_manual
from .scale_manual import scale_size_manual
# position
from .scale_xy import scale_x_discrete, scale_x_continuous
from .scale_xy import scale_y_discrete, scale_y_continuous
# position transforms
from .scale_xy import scale_x_datetime, scale_x_date
from .scale_xy import scale_y_datetime, scale_y_date
from .scale_xy import scale_x_log10, scale_y_log10
from .scale_xy import scale_x_sqrt, scale_y_sqrt
# reverse
from .scale_xy import scale_x_reverse, scale_y_reverse
# format functions
from .utils import dollar, currency, comma, millions
from .utils import percent, scientific
# date helper functions
from .utils import date_breaks, date_format


__all__ = [# color
           'scale_color_brewer', 'scale_colour_brewer',
           'scale_color_distiller', 'scale_colour_distiller',
           'scale_color_gradient', 'scale_colour_gradient',
           'scale_color_gradient2', 'scale_colour_gradient2',
           'scale_color_gradientn', 'scale_colour_gradientn',
           'scale_color_grey', 'scale_colour_grey',
           'scale_color_hue', 'scale_colour_hue',
           'scale_color_discrete', 'scale_color_continuous',
           # fill
           'scale_fill_brewer', 'scale_fill_distiller',
           'scale_fill_gradient', 'scale_fill_gradient2',
           'scale_fill_gradientn', 'scale_fill_grey',
           'scale_fill_hue',
           'scale_fill_discrete', 'scale_fill_continuous',
           # alpha
           'scale_alpha', 'scale_alpha_discrete',
           'scale_alpha_continuous',
           # linetype
           'scale_linetype', 'scale_linetype_discrete',
           'scale_linetype_continuous',
           # shape
           'scale_shape', 'scale_shape_discrete',
           'scale_shape_continuous',
           # size
           'scale_size', 'scale_size_discrete',
           'scale_size_continuous', 'scale_color',
           # identity
           'scale_colour_identity', 'scale_fill_identity',
           'scale_shape_identity', 'scale_linetype_identity',
           'scale_alpha_identity', 'scale_size_identity',
           # manual
           'scale_colour_manual', 'scale_fill_manual',
           'scale_shape_manual', 'scale_linetype_manual',
           'scale_alpha_manual', 'scale_size_manual',
           # position
           'scale_x_discrete', 'scale_x_continuous',
           'scale_y_discrete', 'scale_y_continuous',
           # position transforms
           'scale_x_log10', 'scale_y_log10',
           'scale_x_sqrt', 'scale_y_sqrt',
           # reverse
           'scale_x_reverse', 'scale_y_reverse',
           # position datetime
           'scale_x_datetime', 'scale_x_date',
           'scale_y_datetime', 'scale_y_date',
            # format functions
            'dollar', 'currency', 'comma', 'millions',
            'percent', 'scientific',
            # date helper functions
            'date_breaks', 'date_format',
           ]

__all__ = [str(u) for u in __all__]
