from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, DrawingArea, HPacker, VPacker
import matplotlib.lines as mlines
import operator
import numpy as np


def make_title(title):
    title = title.title()
    return TextArea(" %s " % title, textprops=dict(color="k", fontweight="bold"))

def make_marker_key(label, marker):
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea("  %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(15, 20, 0, 0)
    fontsize = 10
    key = mlines.Line2D([0.5*fontsize], [0.75*fontsize], marker=marker,
                               markersize=(0.5*fontsize), c="k")
    viz.add_artist(key)
    return HPacker(children=[viz, label], align="center", pad=5, sep=0)

def make_size_key(label, size):
    if not isinstance(label, (type(""), type(u""))):
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

def make_linestyle_key(label, style):
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea("  %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(30, 20, 0, 0)
    fontsize = 10
    x = np.arange(0.5, 2.25, 0.25) * fontsize
    y = np.repeat(0.75, 7) * fontsize

    key = mlines.Line2D(x, y, linestyle=style, c="k")
    viz.add_artist(key)
    return HPacker(children=[viz, label], align="center", pad=5, sep=0)

legend_viz = {
    "color": make_line_key,
    "linestyle": make_linestyle_key,
    "marker": make_marker_key,
    "size": make_size_key,
}

def draw_legend(ax, legend, legend_type, legend_title, ith_legend):
    children = []
    children.append(make_title(legend_title))
    viz_handler = legend_viz[legend_type]
    legend_items = sorted(legend.items(), key=operator.itemgetter(1))
    children += [viz_handler(lab, col) for col, lab in legend_items]
    box = VPacker(children=children, align="left", pad=0, sep=5)

    # TODO: The vertical spacing between the legends isn't consistent. Should be
    # padded consistently
    anchored_box = AnchoredOffsetbox(loc=6,
                                     child=box, pad=0.,
                                     frameon=False,
                                     #bbox_to_anchor=(0., 1.02),
                                     # Spacing goes here
                                     bbox_to_anchor=(1, 0.8 - 0.35 * ith_legend),
                                     bbox_transform=ax.transAxes,
                                     borderpad=1.,
                                     )
    return anchored_box

if __name__=="__main__":
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.4, 0.7])

    ax.add_artist(draw_legend(ax,{1: "blah", 2: "blah2", 15: "blah4"}, "size", 1))
    plt.show(block=True)
