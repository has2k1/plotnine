from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .scale_color import scale_color_brewer, scale_colour_brewer
from .scale_color import scale_color_distiller, scale_colour_distiller
from .scale_color import scale_color_gradient, scale_colour_gradient
from .scale_color import scale_color_gradient2, scale_colour_gradient2
from .scale_color import scale_color_gradientn, scale_colour_gradientn
from .scale_color import scale_color_grey, scale_colour_grey
from .scale_color import scale_color_hue, scale_colour_hue
from .scale_color import scale_fill_brewer
from .scale_color import scale_fill_distiller
from .scale_color import scale_fill_gradient
from .scale_color import scale_fill_gradient2
from .scale_color import scale_fill_gradientn
from .scale_color import scale_fill_grey
from .scale_color import scale_fill_hue
from .scale_alpha import scale_alpha
from .scale_alpha import scale_alpha_discrete
from .scale_alpha import scale_alpha_continuous
from .scale_linetype import scale_linetype
from .scale_linetype import scale_linetype_discrete
from .scale_linetype import scale_linetype_continuous
from .scale_shape import scale_shape
from .scale_shape import scale_shape_discrete
from .scale_shape import scale_shape_continuous
from .scale_size import scale_size
from .scale_size import scale_size_discrete
from .scale_size import scale_size_continuous
from .scale_identity import scale_color_identity, scale_colour_identity
from .scale_identity import scale_fill_identity
from .scale_identity import scale_shape_identity
from .scale_identity import scale_linetype_identity
from .scale_identity import scale_alpha_identity
from .scale_identity import scale_size_identity
from .scale_manual import scale_color_manual, scale_colour_manual
from .scale_manual import scale_fill_manual
from .scale_manual import scale_shape_manual
from .scale_manual import scale_linetype_manual
from .scale_manual import scale_alpha_manual
from .scale_manual import scale_size_manual
from .scale_xy import scale_x_discrete, scale_x_continuous
from .scale_xy import scale_y_discrete, scale_y_continuous

# from .scale_colour_brewer import scale_colour_brewer
# from .scale_colour_brewer import scale_colour_brewer as scale_color_brewer
# from .scale_colour_gradient import scale_colour_gradient
# from .scale_colour_gradient import scale_colour_gradient as scale_color_gradient
# from .scale_colour_gradient import scale_colour_gradient as scale_colour_gradient2
# from .scale_colour_gradient import scale_colour_gradient as scale_color_gradient2
# from .scale_colour_manual import scale_colour_manual
# from .scale_colour_manual import scale_colour_manual as scale_color_manual
# from .scale_facet import scale_facet_grid
# from .scale_facet import scale_facet_wrap
# from .scale_x_continuous import scale_x_continuous
# from .scale_x_discrete import scale_x_discrete
# from .scale_x_date import scale_x_date
# from .scale_y_continuous import scale_y_continuous
# from .scale_y_discrete import scale_y_discrete
# from .scale_reverse import scale_y_reverse, scale_x_reverse
# from .scale_log import scale_x_log, scale_y_log
# from .scale_log import scale_x_log as scale_x_log10
# from .scale_log import scale_y_log as scale_y_log10

# __all__ = ['scale_color_brewer', 'scale_colour_brewer',
#            'scale_color_gradient', 'scale_colour_gradient',
#            'scale_colour_gradient2', 'scale_colour_manual', 'scale_facet', 
#            'scale_facet_grid', 'scale_facet_wrap', 'scale_reverse', 
#            'scale_x_continuous', 'scale_x_date', 'scale_x_reverse', 
#            'scale_y_continuous', 'scale_y_reverse', 'scale_x_log',
#            'scale_y_log', 'scale_x_log10', 'scale_y_log10']

__all__ = [# color
           'scale_color_brewer', 'scale_colour_brewer',
           'scale_color_distiller', 'scale_colour_distiller',
           'scale_color_gradient', 'scale_colour_gradient',
           'scale_color_gradient2', 'scale_colour_gradient2',
           'scale_color_gradientn', 'scale_colour_gradientn',
           'scale_color_grey', 'scale_colour_grey',
           'scale_color_hue', 'scale_colour_hue',
           # fill
           'scale_fill_brewer', 'scale_fill_distiller',
           'scale_fill_gradient', 'scale_fill_gradient2',
           'scale_fill_gradientn', 'scale_fill_grey',
           'scale_fill_hue',
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
           ]

__all__ = [str(u) for u in __all__]
