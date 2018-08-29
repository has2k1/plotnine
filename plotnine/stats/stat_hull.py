import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull

from ..doctools import document
from .stat import stat


@document
class stat_hull(stat):
    """
    2 Dimensional Convex Hull

    {usage}

    Parameters
    ----------
    {common_parameters}
    qhull_options: str, optional
        Additional options to pass to Qhull.
        See `Qhull <http://www.qhull.org/>`__ documentation
        for details.

    Raises
    ------
    QhullError
        Raised when Qhull encounters an error condition,
        such as geometrical degeneracy when options to resolve are
        not enabled.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

        'area'  # Area of the convex hull

    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'path', 'position': 'identity',
                      'na_rm': False, 'qhull_options': None}
    CREATES = {'area'}

    @classmethod
    def compute_group(cls, data, scales, **params):
        hull = ConvexHull(
            data[['x', 'y']],
            qhull_options=params['qhull_options'])
        idx = np.hstack([hull.vertices, hull.vertices[0]])

        new_data = pd.DataFrame({
            'x': data['x'].iloc[idx].values,
            'y': data['y'].iloc[idx].values,
            'area': hull.area
        })
        return new_data
