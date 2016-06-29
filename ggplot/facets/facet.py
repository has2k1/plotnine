from __future__ import absolute_import, division, print_function


class facet(object):
    ncol = None
    nrow = None
    as_table = True
    drop = True
    shrink = True
    free = {'x': True, 'y': True}

    def __init__(self, scales='fixed', shrink=True,
                 labeller='label_value', as_table=True,
                 drop=True):
        from .labelling import as_labeller
        self.shrink = shrink
        self.labeller = as_labeller(labeller)
        self.as_table = as_table
        self.drop = drop
        self.free = {'x': scales in ('free_x', 'free'),
                     'y': scales in ('free_y', 'free')}

    def set_breaks_and_labels(self, ranges, layout_info, ax):
        # Add axes and labels on all sides. The super
        # class should remove what is unnecessary

        # limits
        ax.set_xlim(ranges['x_range'])
        ax.set_ylim(ranges['y_range'])

        # breaks
        ax.set_xticks(ranges['x_major'])
        ax.set_yticks(ranges['y_major'])

        # minor breaks
        ax.set_xticks(ranges['x_minor'], minor=True)
        ax.set_yticks(ranges['y_minor'], minor=True)

        # labels
        ax.set_xticklabels(ranges['x_labels'])
        ax.set_yticklabels(ranges['y_labels'])
