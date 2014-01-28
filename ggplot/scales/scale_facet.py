from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# TODO: This is fairly repetiive and can definitely be
# condensed into a lot less code, but it's working for now

import numpy as np
import matplotlib.pyplot as plt
from .utils import calc_axis_breaks
import sys


def scale_facet_wrap(rows, cols, positions, scaletype):
    """Set the scales on each subplot for wrapped faceting.

    Parameters
    ----------
    rows : int 
        number of rows in the faceted plot
    cols : int
        number of columns in the faceted plot
    positions : list of int
        zero-indexed list of faceted plot positions
    scaletype : str or None
        string indicating the type of scaling to apply to the rows and columns
        - None : All plots get the same scale
        - 'free_x' : each plot is free to determine its own x-scale, all plots have the same y-scale
        - 'free_y' : each plot is free to determine its own y-scale, all plots have the same x-scale
        - 'free' : plots are free to determine their own x- and y-scales

    """
    x_extents, y_extents = {}, {}

    # Calculate the extents for the plots
    for pos in positions:
        # Work on the subplot at the current position (adding 1 to pos because
        # matplotlib 1-indexes their subplots)
        
        plt.subplot(rows, cols, pos + 1)

        # Update the x extents for each column

        column, row = 0, 0
        if scaletype in ["free", "free_x"]:
            # If the x scale is free, all plots get their own x scale
            column = pos % cols
            row = int(pos / cols)

        limits = plt.xlim()

        # Get the current bounds for this column. Default lower limit is
        # infinity (because all values < infinity) and the default upper limit
        # is -infinity (because all values > -infinity).
        lower, upper = x_extents.get((column, row), (float("inf"), float("-inf")))

        lower = min(limits[0], lower)
        upper = max(limits[1], upper)

        x_extents[(column, row)] = (lower, upper)

        column, row = 0, 0
        if scaletype in ["free", "free_y"]:
            # If the y scale is free, all plots get their own y scale
            column = pos % cols
            row = int(pos / cols)

        limits = plt.ylim()

        # Get the current bounds for this column. Default lower limit is
        # infinity (because all values < infinity) and the default upper limit
        # is -infinity (because all values > -infinity).
        lower, upper = y_extents.get((column, row), (float("inf"), float("-inf")))

        lower = min(limits[0], lower)
        upper = max(limits[1], upper)

        y_extents[(column, row)] = (lower, upper)

    for pos in positions:
        plt.subplot(rows, cols, pos + 1)
        
        row = int(pos / cols)
        column = pos % cols

        # Find the extents for this position. Default to the extents at
        # position column 0, row 0, in case all plots use the same scale
        xmin, xmax = x_extents[(0, 0)]
        ymin, ymax = y_extents[(0, 0)]
        
        if scaletype in ["free", "free_x"]:
            # If the x scale is free, look up the extents for this column and row
            xmin, xmax = x_extents[(column, row)]

        if scaletype in ["free", "free_y"]:
            # If the y scale is free, look up the extents for this column and row
            ymin, ymax = y_extents[(column, row)]

        x_scale = calc_axis_breaks(xmin, xmax, 4)
        x_scale = np.round(x_scale, 2)

        # Only apply x labels to plots if each plot has its own scale or the
        # plot is in the bottom row of each column.
        x_labs = []
        if scaletype in ["free", "free_x"] or pos in positions[-cols:]:
            x_labs = x_scale

        plt.xticks(x_scale, x_labs)

        # Set the y-axis scale and labels
        y_scale = calc_axis_breaks(ymin, ymax, 4)
        y_scale = np.round(y_scale, 2)

        # Only apply y labels to plots if each plot has its own scale or the
        # plot is in the left column.
        y_labs = []
        if scaletype in ["free", "free_y"] or column == 0:
            y_labs = y_scale

        plt.yticks(y_scale, y_labs)

def scale_facet_grid(xdim, ydim, facet_pairs, scaletype):
    # everyone gets the same scales
    if scaletype is None:
        min_x, max_x = 999999999, -999999999
        min_y, max_y = 999999999, -999999999
        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            min_x = min(min_x, min(plt.xticks()[0]))
            max_x = max(max_x, max(plt.xticks()[0]))
            min_y = min(min_y, min(plt.yticks()[0]))
            max_y = max(max_y, max(plt.yticks()[0]))

        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            y_scale = calc_axis_breaks(min_y, max_y, 4)
            y_scale = np.round(y_scale, 2)
            y_labs = y_scale
            if pos % ydim!=1:
                y_labs = []
            plt.yticks(y_scale, y_labs)
            
            x_scale = calc_axis_breaks(min_x, max_x, 4)
            x_scale = np.round(x_scale, 2)
            x_labs = x_scale
            if pos <= (len(facet_pairs) - ydim):
                x_labs = []
            plt.xticks(x_scale, x_labs)

    elif scaletype=="free_y":
        min_x, max_x = 999999999, -999999999
        min_ys, max_ys = {}, {}

        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            y_bucket = int((pos-1) / ydim)

            min_ys[y_bucket] = min_ys.get(y_bucket, 999999999)
            max_ys[y_bucket] = max_ys.get(y_bucket, -999999999)

            min_x = min(min_x, min(plt.xticks()[0]))
            max_x = max(max_x, max(plt.xticks()[0]))
            min_ys[y_bucket] = min(min_ys[y_bucket], min(plt.yticks()[0]))
            max_ys[y_bucket] = max(max_ys[y_bucket], max(plt.yticks()[0]))
        
        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            y_bucket = int((pos-1) / ydim)

            y_scale = calc_axis_breaks(min_ys[y_bucket], max_ys[y_bucket], 4)
            y_scale = np.round(y_scale, 2)
            y_labs = y_scale
            if pos % ydim!=1:
                y_labs = []
            plt.yticks(y_scale, y_labs)
            
            x_scale = calc_axis_breaks(min_x, max_x, 4)
            x_scale = np.round(x_scale, 2)
            x_labs = x_scale
            if pos <= (len(facet_pairs) - ydim):
                x_labs = []
            plt.xticks(x_scale, x_labs)

    elif scaletype=="free_x":
        min_y, max_y = 999999999, -999999999
        min_xs, max_xs = {}, {}

        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            x_bucket = int((pos-1) / xdim)

            min_xs[x_bucket] = min_xs.get(x_bucket, 999999999)
            max_xs[x_bucket] = max_xs.get(x_bucket, -999999999)

            min_y = min(min_y, min(plt.yticks()[0]))
            max_y = max(max_y, max(plt.yticks()[0]))
            min_xs[x_bucket] = min(min_xs[x_bucket], min(plt.xticks()[0]))
            max_xs[x_bucket] = max(max_xs[x_bucket], max(plt.xticks()[0]))
        
        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            x_bucket = int((pos-1) / xdim)

            x_scale = calc_axis_breaks(min_xs[x_bucket], max_xs[x_bucket], 4)
            x_scale = np.round(x_scale, 2)
            x_labs = x_scale
            if pos <= ((len(facet_pairs) - ydim)):
                x_labs = []
            plt.xticks(x_scale, x_labs)
            
            y_scale = calc_axis_breaks(min_y, max_y, 4)
            y_scale = np.round(y_scale, 2)
            y_labs = y_scale
            if pos % ydim!=1:
                y_labs = []
            plt.yticks(y_scale, y_labs)
    
    else:
        min_xs, max_xs = {}, {}
        min_ys, max_ys = {}, {}

        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            x_bucket = int((pos-1) / xdim)
            min_xs[x_bucket] = min_xs.get(x_bucket, 999999999)
            max_xs[x_bucket] = max_xs.get(x_bucket, -999999999)

            min_xs[x_bucket] = min(min_xs[x_bucket], min(plt.xticks()[0]))
            max_xs[x_bucket] = max(max_xs[x_bucket], max(plt.xticks()[0]))

            y_bucket = int((pos-1) / ydim)
            min_ys[y_bucket] = min_ys.get(y_bucket, 999999999)
            max_ys[y_bucket] = max_ys.get(y_bucket, -999999999)

            min_ys[y_bucket] = min(min_ys[y_bucket], min(plt.yticks()[0]))
            max_ys[y_bucket] = max(max_ys[y_bucket], max(plt.yticks()[0]))
        
        for pos, _ in enumerate(facet_pairs):
            pos += 1
            plt.subplot(xdim, ydim, pos)
            
            x_bucket = int((pos-1) / xdim)

            x_scale = calc_axis_breaks(min_xs[x_bucket], max_xs[x_bucket], 4)
            x_scale = np.round(x_scale, 2)
            x_labs = x_scale
            if pos <= ((len(facet_pairs) - ydim)):
                x_labs = []
            plt.xticks(x_scale, x_labs)
            y_bucket = int((pos-1) / ydim)

            y_scale = calc_axis_breaks(min_ys[y_bucket], max_ys[y_bucket], 4)
            y_scale = np.round(y_scale, 2)
            y_labs = y_scale
            if pos % ydim!=1:
                y_labs = []
            plt.yticks(y_scale, y_labs)
            
