import matplotlib.pyplot as plt
import numpy as np

def scale_facet(scale_type, positions, n_wide, n_high):
    if scale_type=="free":
        return
    else:
        return
    xticks, yticks = [], []
    for pos in positions:
        plt.subplot(n_wide, n_high, pos)
        if scale_type=="free_x":
            yticks.append(plt.yticks())
        elif scale_type=="free_y":
            xticks.append(plt.xticks())
    
    print xticks
    print yticks

