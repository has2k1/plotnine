from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook

from .geom import geom
from ggplot.utils import is_string

class geom_boxplot(geom):
    DEFAULT_AES = {'y': None, 'color': 'black', 'flier_marker': '+'}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    def __group(self, x, y):
        out = {}
        for xx, yy in zip(x,y):
            if yy not in out: out[yy] = []
            out[yy].append(xx)
        return out

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        color = pinfo.pop('color')
        fliermarker = pinfo.pop('flier_marker')

        if y is not None:
            g = self.__group(x,y)
            l = sorted(g.keys())
            x = [g[k] for k in l]
            plt.setp(ax, yticklabels=l)

        q = ax.boxplot(x, vert=False)
        plt.setp(q['boxes'], color=color)
        plt.setp(q['whiskers'], color=color)
        plt.setp(q['fliers'], color=color, marker=fliermarker)
