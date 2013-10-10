from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, DrawingArea, HPacker, VPacker
import matplotlib.lines as mlines 
import operator

def make_title(title):
    title = title.title()
    return TextArea(" %s " % title, textprops=dict(color="k", fontweight="bold"))

def make_marker_key(label, marker):
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea(": %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(15, 20, 0, 0)
    fontsize = 10
    key = mlines.Line2D([0.5*fontsize], [0.75*fontsize], marker=marker, 
                               markersize=(0.5*fontsize), c="k")
    viz.add_artist(key)
    return HPacker(children=[viz, label], align="center", pad=5, sep=0)

def make_line_key(label, color):
    label = str(label)
    idx = len(label)
    pad = 20 - idx
    lab = label[:max(idx, 20)]
    pad = " "*pad
    label = TextArea(": %s" % lab, textprops=dict(color="k"))
    viz = DrawingArea(20, 20, 0, 0)
    viz.add_artist(Rectangle((0, 5), width=16, height=5, fc=color))
    return HPacker(children=[viz, label], height=25, align="center", pad=5, sep=0)

legend_viz = {
    "color": make_line_key,
    "marker": make_marker_key 
}

def draw_legend(ax, legend, legend_type, ith_legend):
    children = []
    children.append(make_title(legend_type))
    viz_handler = legend_viz[legend_type]
    legend_items = sorted(legend.iteritems(), key=operator.itemgetter(1))
    children += [viz_handler(lab, col) for col, lab in legend_items]
    box = VPacker(children=children, align="left", pad=0, sep=5)

    anchored_box = AnchoredOffsetbox(loc=6,
                                     child=box, pad=0.,
                                     frameon=True,
                                     #bbox_to_anchor=(0., 1.02),
                                     bbox_to_anchor=(1, 0.8 - 0.45 * ith_legend),
                                     bbox_transform=ax.transAxes,
                                     borderpad=1.,
                                     )
    return anchored_box
