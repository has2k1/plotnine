# TODO: This is fairly repetiive and can definitely be
# condensed into a lot less code, but it's working for now

import numpy as np
import matplotlib.pyplot as plt
from utils import calc_axis_breaks

def scale_facet(xdim, ydim, facet_pairs, scaletype):
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
            
