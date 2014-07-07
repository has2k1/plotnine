from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.patches import Rectangle
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, DrawingArea, HPacker, VPacker
from collections import defaultdict
import matplotlib.lines as mlines
import numpy as np


"""
A legend is a dict of type

{aesthetic: {
    'column_name': 'column-name-in-the-dataframe',
    'dict': {visual_value: legend_key},
    'scale_type': 'discrete' | 'continuous'}}

where aesthetic is one of:
  'color', 'fill', 'shape', 'size', 'linetype', 'alpha'

visual_value is a:
  color value, fill color value, linetype string,
  shape character, size value, alpha value

legend_key is either:
  - quantile-value for continuous mappings.
  - value for discrete mappings.
"""


def add_legend(legend, ax):
    """
    Add a legend to the axes

    Parameters
    ----------
    legend: dictionary
        Specification in components.legend.py
    ax: axes
    """
    # Group legends by column name and invert color/label mapping
    groups = {}
    for aesthetic in legend:
        legend_entry = legend[aesthetic]
        column_name = legend_entry["column_name"]
        g = groups.get(column_name, {})
        legend_dict = { l:c for c,l in legend_entry['dict'].items() }
        g[aesthetic] = defaultdict(lambda : None, legend_dict)
        groups[column_name] = g

    nb_rows = 0
    nb_cols = 0
    max_rows = 20
    # py3 and py2 have different sorting order in dics,
    # so make that consistent
    for i, column_name in enumerate(sorted(groups.keys())):
        legend_group = groups[column_name]
        legend_box, rows = draw_legend_group(legend_group, column_name, i)
        cur_nb_rows = nb_rows
        nb_rows += rows + 1
        if nb_rows > max(max_rows, rows + 1) :
            nb_cols += 1
            nb_rows = 0
            cur_nb_rows = 0
        anchor_legend(ax, legend_box, cur_nb_rows, nb_cols)


def draw_legend_group(legends, column_name, ith_group):
    labels              = get_legend_labels(legends)
    colors, has_color   = get_colors(legends)
    alphas, has_alpha   = get_alphas(legends)
    legend_title        = make_title(column_name)
    legend_labels       = [make_label(l) for l in labels]
    none_dict           = defaultdict(lambda : None)
    legend_cols         = []

    # Draw shapes if any (discs for sizes)
    if "shape" in legends or "size" in legends :
        shapes = legends["shape"] if "shape" in legends else none_dict
        sizes = legends["size"] if "size" in legends else none_dict
        line = lambda l : make_shape(colors[l], shapes[l], sizes[l], alphas[l])
        legend_shapes = [line(label) for label in labels]
        legend_cols.append(legend_shapes)

    # Draw lines if any
    if "linetype" in legends :
        linetypes = legends["linetype"]
        legend_lines = [make_line(colors[l], linetypes[l], alphas[l])
                        for l in labels]
        legend_cols.append(legend_lines)

    # If we don't have lines, legends or sizes, indicate color with a rectangle
    already_drawn = set(["linetype", "shape", "size"])
    if (len(already_drawn.intersection(legends)) == 0
        and (has_color or has_alpha)) :
        legend_rects = [make_rect(colors[l], alphas[l]) for l in labels]
        legend_cols.append(legend_rects)

    # Concatenate columns and compile rows
    legend_cols.append(legend_labels)
    row = lambda l : HPacker(children=l, height=25, align='center', pad=5, sep=0)
    legend_rows = [row(legend_items) for legend_items in zip(*legend_cols)]

    # Vertically align items and anchor in plot
    rows = [legend_title] + legend_rows
    box = VPacker(children=rows, align="left", pad=0, sep=-10)
    return box, len(rows)



def anchor_legend(ax, box, row, col):
    anchored = AnchoredOffsetbox(loc=2,
                                 child=box,
                                 pad=0.,
                                 frameon=False,
                                 bbox_to_anchor=(1 + 0.25*col, 1 - 0.054*row),
                                 bbox_transform=ax.transAxes,
                                 )
    # Workaround for a bug in matplotlib up to 1.3.1
    # https://github.com/matplotlib/matplotlib/issues/2530
    anchored.set_clip_on(False)
    ax.add_artist(anchored)



def make_title(title):
    title = title.title()
    area = TextArea(" %s " % title, textprops=dict(color="k", fontweight="bold"))
    viz = DrawingArea(20, 10, 0, 0)
    packed = VPacker(children=[area, viz], align="center", pad=0, sep=0)
    return packed



def make_shape(color, shape, size, alpha, y_offset = 10, height = 20):
    color = color if color != None else "k" # Default value if None
    shape = shape if shape != None else "o"
    size = size*0.6+45 if size != None else 75
    viz = DrawingArea(30, height, 8, 1)
    key = mlines.Line2D([0], [y_offset], marker=shape, markersize=size/12.0,
                        mec=color, c=color, alpha=alpha)
    viz.add_artist(key)
    return viz



def make_line(color, style, alpha, width = 20,
              y_offset = 10, height = 20, linewidth = 3):
    color = color if color != None else "k" # Default value if None
    style = style if style != None else "-"
    viz = DrawingArea(30, 10, 0, -5)
    x = np.arange(0.0, width, width/7.0)
    y = np.repeat(y_offset, x.size)
    key = mlines.Line2D(x, y, linestyle=style, linewidth=linewidth,
                        alpha=alpha, c=color)
    viz.add_artist(key)
    return viz



def make_rect(color, alpha, size = (20,6), height = 20):
    color = color if color != None else "k" # Default value if None
    viz = DrawingArea(30, height, 0, 1)
    viz.add_artist(Rectangle((0, 6), width=size[0], height=size[1],
                             alpha=alpha, fc=color))
    return viz



def make_label(label, max_length = 20, capitalize = True):
    label_text = str(label).title()[:max_length]
    label_area = TextArea(label_text, textprops=dict(color="k"))
    return label_area


def get_legend_labels(legends) :
    # All the legends are for the same column, so the labels of any will do
    return sorted(list(legends.values())[0].keys())


def get_colors(legends) :
    if "color" in legends :
        return legends["color"], True
    elif "fill" in legends :
        return legends["fill"], True
    else :
        return defaultdict(lambda : None), False


def get_alphas(legends) :
    if "alpha" in legends :
        return legends["alpha"], True
    else :
        return defaultdict(lambda : 1), False


def get_labels(data,
               label_col,
               scale_type = None,
               discrete_limit = 8,
               quant_indices = [0, 25, 50, 75, 100]) :
    """
    Decides whether a legend should be discrete or continuous and returns
    the appropriate legend labels based on the data.

    Parameters
    ----------
    data : DataFrame
        The general Dataframe containing plot data
    label_col : string
        The column this aspect of the legend is assigned to
    scale_type : Maybe string but can be None
        "continuous" if we want to force a continuous legend
        "discrete" if we want to force a discrete legend
    quand_indices : [Int]
        For the continuous case we can specify which (an how many)
        percentiles we want to map from the data. Default is:
            [0, 25, 50, 75, 100]

    Returns
    -------
    labels: [String], the labels
    scale_type: string
        The type of legend we ended up with. Can be "continuous" or
        "discrete"
    quant_indices : For the case of continuous we return the percentiles used
    """
    if scale_type == "continuous" :
        return continuous_labels(data[label_col], quant_indices)
    elif scale_type == "discrete" :
        return discrete_labels(data[label_col])
    else :
        # Figure out whether the data looks continuous or discrete
        uniques = set(np.unique(data[label_col]))
        numeric_cols = set(data._get_numeric_data().columns)
        bool_cols = set(data._get_bool_data().columns)
        continuous_cols = numeric_cols - bool_cols
        if len(uniques) > discrete_limit and label_col in continuous_cols :
            return continuous_labels(data[label_col], quant_indices)
        else :
            return discrete_labels(data[label_col])

def continuous_labels(data, quant_indices = [0, 25, 50, 75, 100]) :
    labels = np.percentile(data, quant_indices)
    return labels, "continuous", quant_indices

def discrete_labels(data) :
    labels = np.unique(data)
    return labels, "discrete", []


