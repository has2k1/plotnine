from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from .stat import stat

_MSG_LABELS = """There are more than 30 unique values mapped to x.
    If you want a histogram instead, use 'geom_histogram()'.
"""

class stat_bar(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'bar', 'position': 'stack',
                      'width': 0.9, 'drop': False,
                      'origin': None, 'labels': None}


    def _calculate(self, data):
        # reorder x according to the labels
        new_data = pd.DataFrame()
        new_data["x"] = self.labels
        for column in set(data.columns) - set('x'):
            column_dict = dict(zip(data["x"],data[column]))
            default = 0 if column == "y" else data[column].values[0]
            new_data[column] = [column_dict.get(val, default)
                                for val in self.labels]
        return new_data


    def _calculate_global(self, data):
        labels = self.params['labels']
        if labels == None:
            labels = sorted(set(data['x'].values))
        # For a lot of labels, put out a warning
        if len(labels) > 30:
            self._print_warning(_MSG_LABELS)
        # Check if there is a mapping
        self.labels = labels

