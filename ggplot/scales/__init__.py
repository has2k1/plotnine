from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .scale_colour_brewer import scale_colour_brewer
from .scale_colour_brewer import scale_colour_brewer as scale_color_brewer
from .scale_colour_gradient import scale_colour_gradient
from .scale_colour_gradient import scale_colour_gradient as scale_color_gradient
from .scale_colour_gradient import scale_colour_gradient as scale_colour_gradient2
from .scale_colour_gradient import scale_colour_gradient as scale_color_gradient2
from .scale_colour_manual import scale_colour_manual
from .scale_colour_manual import scale_colour_manual as scale_color_manual
from .scale_x_continuous import scale_x_continuous
from .scale_x_discrete import scale_x_discrete
from .scale_x_date import scale_x_date
from .scale_y_continuous import scale_y_continuous
from .scale_y_discrete import scale_y_discrete
from .scale_reverse import scale_y_reverse, scale_x_reverse
from .scale_log import scale_x_log, scale_y_log
from .scale_log import scale_x_log as scale_x_log10
from .scale_log import scale_y_log as scale_y_log10

__all__ = ['scale_colour_brewer', 'scale_color_brewer',
           'scale_colour_gradient', 'scale_color_gradient',
           'scale_colour_gradient2', 'scale_color_gradient2', 
           'scale_colour_manual', 'scale_color_manual',
           'scale_x_continuous', 'scale_y_continuous',
           'scale_x_discrete', 'scale_y_discrete',
           'scale_x_reverse','scale_y_reverse', 
           'scale_x_date', # scale_y_date is missing
           'scale_x_log', 'scale_y_log',
           'scale_x_log10', 'scale_y_log10']
__all__ = [str(u) for u in __all__]
