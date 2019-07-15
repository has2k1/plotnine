# alpha
from .scale_alpha import scale_alpha
from .scale_alpha import scale_alpha_continuous
from .scale_alpha import scale_alpha_ordinal
from .scale_alpha import scale_alpha_discrete
from .scale_alpha import scale_alpha_datetime
# color
from .scale_color import scale_color_brewer, scale_colour_brewer
from .scale_color import scale_color_cmap, scale_colour_cmap
from .scale_color import scale_color_cmap_d, scale_colour_cmap_d
from .scale_color import scale_color_ordinal, scale_colour_ordinal
from .scale_color import scale_color_continuous, scale_colour_continuous
from .scale_color import scale_color_desaturate, scale_colour_desaturate
from .scale_color import scale_color_discrete, scale_colour_discrete
from .scale_color import scale_color_distiller, scale_colour_distiller
from .scale_color import scale_color_gradient, scale_colour_gradient
from .scale_color import scale_color_gradient2, scale_colour_gradient2
from .scale_color import scale_color_gradientn, scale_colour_gradientn
from .scale_color import scale_color_grey, scale_colour_grey
from .scale_color import scale_color_gray, scale_colour_gray
from .scale_color import scale_color_hue, scale_colour_hue
from .scale_color import scale_color_datetime, scale_colour_datetime
# fill
from .scale_color import scale_fill_brewer
from .scale_color import scale_fill_cmap
from .scale_color import scale_fill_cmap_d
from .scale_color import scale_fill_ordinal
from .scale_color import scale_fill_continuous
from .scale_color import scale_fill_desaturate
from .scale_color import scale_fill_discrete
from .scale_color import scale_fill_distiller
from .scale_color import scale_fill_gradient
from .scale_color import scale_fill_gradient2
from .scale_color import scale_fill_gradientn
from .scale_color import scale_fill_grey, scale_fill_gray
from .scale_color import scale_fill_hue
from .scale_color import scale_fill_datetime
# identity
from .scale_identity import scale_alpha_identity
from .scale_identity import scale_color_identity, scale_colour_identity
from .scale_identity import scale_fill_identity
from .scale_identity import scale_linetype_identity
from .scale_identity import scale_shape_identity
from .scale_identity import scale_size_identity
# linetype
from .scale_linetype import scale_linetype
from .scale_linetype import scale_linetype_continuous
from .scale_linetype import scale_linetype_discrete
# manual
from .scale_manual import scale_alpha_manual
from .scale_manual import scale_color_manual, scale_colour_manual
from .scale_manual import scale_fill_manual
from .scale_manual import scale_linetype_manual
from .scale_manual import scale_shape_manual
from .scale_manual import scale_size_manual
# shape
from .scale_shape import scale_shape
from .scale_shape import scale_shape_continuous
from .scale_shape import scale_shape_discrete
# size
from .scale_size import scale_size
from .scale_size import scale_size_area
from .scale_size import scale_size_continuous
from .scale_size import scale_size_ordinal
from .scale_size import scale_size_discrete
from .scale_size import scale_size_radius
from .scale_size import scale_size_datetime
# stroke
from .scale_stroke import scale_stroke
from .scale_stroke import scale_stroke_continuous
from .scale_stroke import scale_stroke_discrete
# xy position and transforms
from .scale_xy import scale_x_datetime, scale_x_date
from .scale_xy import scale_x_discrete, scale_x_continuous
from .scale_xy import scale_x_log10, scale_y_log10
from .scale_xy import scale_x_reverse, scale_y_reverse
from .scale_xy import scale_x_sqrt, scale_y_sqrt
from .scale_xy import scale_x_timedelta
from .scale_xy import scale_y_datetime, scale_y_date
from .scale_xy import scale_y_discrete, scale_y_continuous
from .scale_xy import scale_y_timedelta
# limits
from .limits import xlim, ylim, lims, expand_limits


__all__ = [
           # color
           'scale_color_brewer', 'scale_colour_brewer',
           'scale_color_cmap', 'scale_colour_cmap',
           'scale_color_cmap_d', 'scale_colour_cmap_d',
           'scale_color_ordinal', 'scale_colour_ordinal',
           'scale_color_continuous', 'scale_colour_continuous',
           'scale_color_discrete', 'scale_colour_discrete',
           'scale_color_distiller', 'scale_colour_distiller',
           'scale_color_desaturate', 'scale_colour_desaturate',
           'scale_color_gradient', 'scale_colour_gradient',
           'scale_color_gradient2', 'scale_colour_gradient2',
           'scale_color_gradientn', 'scale_colour_gradientn',
           'scale_color_grey', 'scale_colour_grey',
           'scale_color_gray', 'scale_colour_gray',
           'scale_color_hue', 'scale_colour_hue',
           'scale_color_datetime', 'scale_colour_datetime',
           # fill
           'scale_fill_brewer', 'scale_fill_cmap',
           'scale_fill_cmap_d',
           'scale_fill_ordinal',
           'scale_fill_continuous',
           'scale_fill_desaturate', 'scale_fill_discrete',
           'scale_fill_distiller', 'scale_fill_gradient',
           'scale_fill_gradient2', 'scale_fill_gradientn',
           'scale_fill_grey', 'scale_fill_gray',
           'scale_fill_hue', 'scale_fill_datetime',
           # alpha
           'scale_alpha', 'scale_alpha_discrete',
           'scale_alpha_ordinal',
           'scale_alpha_continuous', 'scale_alpha_datetime',
           # linetype
           'scale_linetype', 'scale_linetype_discrete',
           'scale_linetype_continuous',
           # shape
           'scale_shape', 'scale_shape_discrete',
           'scale_shape_continuous',
           # size
           'scale_size', 'scale_size_area',
           'scale_size_discrete', 'scale_size_continuous',
           'scale_size_ordinal',
           'scale_size_radius', 'scale_size_datetime',
           # stroke
           'scale_stroke', 'scale_stroke_continuous',
           'scale_stroke_discrete',
           # identity
           'scale_alpha_identity', 'scale_color_identity',
           'scale_colour_identity', 'scale_fill_identity',
           'scale_linetype_identity', 'scale_shape_identity',
           'scale_size_identity',
           # manual
           'scale_color_manual', 'scale_colour_manual',
           'scale_fill_manual', 'scale_shape_manual',
           'scale_linetype_manual', 'scale_alpha_manual',
           'scale_size_manual',
           # xy position and transforms
           'scale_x_continuous', 'scale_x_date',
           'scale_x_datetime', 'scale_x_discrete',
           'scale_x_log10', 'scale_x_reverse',
           'scale_x_sqrt', 'scale_x_timedelta',
           'scale_y_continuous', 'scale_y_date',
           'scale_y_datetime', 'scale_y_discrete',
           'scale_y_log10', 'scale_y_reverse',
           'scale_y_sqrt', 'scale_y_timedelta',
           # limits
           'xlim', 'ylim', 'lims', 'expand_limits'
           ]
