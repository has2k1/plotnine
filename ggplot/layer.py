from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .components.aes import aes, is_calculated_aes
from .scales.scales import scales_add_defaults


class layer(object):

    def __init__(self, geom=None, stat=None,
                 data=None, mapping=None,
                 position=None, params=None,
                 inherit_aes=False, group=None):
        self.geom = geom
        self.stat = stat
        self.data = data
        self.mapping = mapping
        self.position = position
        self.params = params
        self.inherit_aes = inherit_aes
        self.group = group

    def layer_mapping(self, mapping):
        """
        Return the mappings that are active in this layer
        """
        # For certain geoms, it is useful to be able to
        # ignore the default aesthetics and only use those
        # set in the layer
        if self.inherit_aes:
            # TODO: Changing this accordingly
            aesthetics = mapping
        else:
            aesthetics = mapping

        # drop aesthetics that are manual or calculated
        manual = set(self.geom.manual_aes.keys())
        calculated = set(is_calculated_aes(aesthetics))
        d = dict((ae, v) for ae, v in aesthetics.items()
                 if not (ae in manual) and not (ae in calculated))
        return aes(**d)


    def compute_aesthetics(self, data, plot):
        aesthetics = self.layer_mapping(plot.mapping)

        # Override grouping if set in layer.
        if not self.group is None:
            aesthetics['group'] = self.group

        scales_add_defaults(plot.scales, data, aesthetics)

        return data

"""
  compute_aesthetics <- function(., data, plot) {
    aesthetics <- .$layer_mapping(plot$mapping)

    if (!is.null(.$subset)) {
      include <- data.frame(eval.quoted(.$subset, data, plot$env))
      data <- data[rowSums(include, na.rm = TRUE) == ncol(include), ]
    }

    # Override grouping if set in layer.
    if (!is.null(.$geom_params$group)) {
      aesthetics["group"] <- .$geom_params$group
    }

    scales_add_defaults(plot$scales, data, aesthetics, plot$plot_env)

    # Evaluate aesthetics in the context of their data frame
    evaled <- compact(
      eval.quoted(aesthetics, data, plot$plot_env))

    lengths <- vapply(evaled, length, integer(1))
    n <- if (length(lengths) > 0) max(lengths) else 0

    wrong <- lengths != 1 & lengths != n
    if (any(wrong)) {
      stop("Aesthetics must either be length one, or the same length as the data",
        "Problems:", paste(aesthetics[wrong], collapse = ", "), call. = FALSE)
    }

    if (empty(data) && n > 0) {
      # No data, and vectors suppled to aesthetics
      evaled$PANEL <- 1
    } else {
      evaled$PANEL <- data$PANEL
    }
    data.frame(evaled)
  }
"""
