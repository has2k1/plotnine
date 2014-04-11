from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, DrawingArea, HPacker, VPacker
import matplotlib.lines as mlines
import operator
import numpy as np

import six

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

def make_title(title):
    title = title.title()
    return TextArea(" %s " % title, textprops=dict(color="k", fontweight="bold"))

def make_shape_key(label, shape):
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea("  %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(15, 20, 0, 0)
    fontsize = 10
    key = mlines.Line2D([0.5*fontsize], [0.75*fontsize], marker=shape,
                               markersize=(0.5*fontsize), c="k")
    viz.add_artist(key)
    return HPacker(children=[viz, label], align="center", pad=5, sep=0)

def make_size_key(label, size):
    if not isinstance(label, six.string_types):
        label = round(label, 2)
        label = str(label)
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea("  %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(15, 20, 0, 0)
    fontsize = 10
    key = mlines.Line2D([0.5*fontsize], [0.75*fontsize], marker="o",
                               markersize=size / 20., c="k")
    viz.add_artist(key)
    return HPacker(children=[viz, label], align="center", pad=5, sep=0)

# TODO: Modify to correctly handle both, color and fill
# to include an alpha
def make_line_key(label, color):
    label = str(label)
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea("  %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(20, 20, 0, 0)
    viz.add_artist(Rectangle((0, 5), width=16, height=5, fc=color))
    return HPacker(children=[viz, label], height=25, align="center", pad=5, sep=0)

def make_linetype_key(label, linetype):
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea("  %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(30, 20, 0, 0)
    fontsize = 10
    x = np.arange(0.5, 2.25, 0.25) * fontsize
    y = np.repeat(0.75, 7) * fontsize

    key = mlines.Line2D(x, y, linestyle=linetype, c="k")
    viz.add_artist(key)
    return HPacker(children=[viz, label], align="center", pad=5, sep=0)

legend_viz = {
    "color": make_line_key,
    "fill": make_line_key,
    "linetype": make_linetype_key,
    "shape": make_shape_key,
    "size": make_size_key,
}

def add_legend(legend, ax):
    """
    Add a legend to the axes

    Parameters
    ----------
    legend: dictionary
        Specification in components.legend.py
    ax: axes
    """
    # TODO: Implement alpha
    # It should be coupled with fill, if fill is not
    # part of the aesthetics, then with color
    remove_alpha = 'alpha' in legend
    if remove_alpha:
        _alpha_entry = legend.pop('alpha')

    # py3 and py2 have different sorting order in dics,
    # so make that consistent
    for i, aesthetic in enumerate(sorted(legend.keys())):
        legend_entry = legend[aesthetic]
        new_legend = draw_entry(ax, legend_entry, aesthetic, i)
        ax.add_artist(new_legend)

    if remove_alpha:
        legend['alpha'] = _alpha_entry

def draw_entry(ax, legend_entry, aesthetic, ith_entry):
    children = []
    children.append(make_title(legend_entry['column_name']))
    viz_handler = legend_viz[aesthetic]
    legend_items = sorted(legend_entry['dict'].items(), key=operator.itemgetter(1))
    children += [viz_handler(str(lab), col) for col, lab in legend_items]
    box = VPacker(children=children, align="left", pad=0, sep=5)

    # TODO: The vertical spacing between the legends isn't consistent. Should be
    # padded consistently
    anchored_box = AnchoredOffsetbox(loc=6,
                                     child=box, pad=0.,
                                     frameon=False,
                                     #bbox_to_anchor=(0., 1.02),
                                     # Spacing goes here
                                     bbox_to_anchor=(1, 0.8 - 0.35 * ith_entry),
                                     bbox_transform=ax.transAxes,
                                     borderpad=1.,
                                     )
    # Workaround for a bug in matplotlib up to 1.3.1
    # https://github.com/matplotlib/matplotlib/issues/2530
    anchored_box.set_clip_on(False)
    return anchored_box

if __name__=="__main__":
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.4, 0.7])

    ax.add_artist(draw_legend(ax,{1: "blah", 2: "blah2", 15: "blah4"}, "size", 1))
    plt.show(block=True)
