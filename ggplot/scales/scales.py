from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import textwrap
import itertools

import numpy as np

import ggplot.scales  # TODO: make relative
from ..utils import discrete_dtypes, continuous_dtypes


class Scales(list):
    def find(self, aesthetic):
        """
        Return a list of True|False
        """
        return [aesthetic in s.aesthetics for s in self]

    def input(self):
        """
        Return a list of all the aesthetics covered by
        the scales
        """
        lst = [s.aesthetics for s in self]
        return list(itertools.chain(lst))

    def get_scales(self, aesthetic):
        """
        Return the scale for the aesthetic or None if there
        isn't one.
        """
        bool_lst = self.find(aesthetic)
        try:
            return bool_lst.index(True)
        except ValueError:
            return None

    def non_position_scales(self):
        """
        Return a list of the non-position scales that
        are present
        """
        l = [s for s in self
             if not ('x' in s.aesthetics) and not ('y' in s.aesthetics)]
        return Scales(l)


"""
  find = function(aesthetic) {
    vapply(scales, function(x) any(aesthetic %in% x$aesthetics), logical(1))
  },
  has_scale = function(aesthetic) {
    any(find(aesthetic))
  },
  add = function(scale) {
    prev_aes <- find(scale$aesthetics)
    if (any(prev_aes)) {
      # Get only the first aesthetic name in the returned vector -- it can
      # sometimes be c("x", "xmin", "xmax", ....)
      scalename <- scales[prev_aes][[1]]$aesthetics[1]
      message("Scale for '", scalename,
        "' is already present. Adding another scale for '", scalename,
        "', which will replace the existing scale.")
    }

    # Remove old scale for this aesthetic (if it exists)
    scales <<- c(scales[!prev_aes], list(scale))
  },
  clone = function() {
    new_scales <- lapply(scales, scale_clone)
    Scales$new(new_scales)
  },
  n = function() {
    length(scales)
  },
  input = function() {
    unlist(lapply(scales, "[[", "aesthetics"))
  },
  initialize = function(scales = NULL) {
    initFields(scales = scales)
  },
  non_position_scales = function(.) {
    Scales$new(scales[!find("x") & !find("y")])
  },
  get_scales = function(output) {
    scale <- scales[find(output)]
    if (length(scale) == 0) return()
    scale[[1]]
  }
"""

def scales_add_defaults(scales, data, aesthetics):
    """
    Add default scales for the aesthetics if none are
    present
    """
    new_scales = []
    if not aesthetics:
        return

    # aesthetics with scales
    if scales:
        aws = reduce(set.union, map(set, [sc.aesthetics for sc in scales]))
    else:
        aws = set()

    # aesthetics that do not have scales present
    new_aesthetics = set(aesthetics.keys()) - aws
    if not new_aesthetics:
        return

    ae_cols = [(ae, aesthetics[ae]) for ae in new_aesthetics
                 if aesthetics[ae] in data.columns]
    for ae, col in ae_cols:
        _type = scale_type(data[col])
        scale_name = 'scale_{}_{}'.format(ae, _type)

        try:
            scale_f = getattr(ggplot.scales, scale_name)
        except AttributeError:
            # Skip aesthetics with no scales (e.g. group, order, etc)
            continue
        scales.append(scale_f())


def scale_type(column):
    if column.dtype in continuous_dtypes:
        stype = 'continuous'
    elif column.dtype in discrete_dtypes:
        stype = 'discrete'
    elif column.dtype == np.dtype('<M8[ns]'):
        stype = 'datetime'
    else:
        msg = """\
            Don't know how to automatically pick scale for \
            object of type {}. Defaulting to 'continuous'""".format(
                column.dtype)
        sys.stderr.write(textwrap.dedent(msg))
        stype = 'continuous'
    return stype
