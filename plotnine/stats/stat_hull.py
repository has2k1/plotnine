import numpy as np

from .._utils import frame
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
    qhull_options: str, default=None
        Additional options to pass to Qhull.
        See `Qhull <http://www.qhull.org/>`__ documentation
        for details.

    Raises
    ------
    scipy.spatial.QhullError
        Raised when Qhull encounters an error condition,
        such as geometrical degeneracy when options to resolve are
        not enabled.

    See Also
    --------
    plotnine.geom_path : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "area"  # Area of the convex hull
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {"geom": "path", "qhull_options": None}
    CREATES = {"area"}

    def compute_group(self, data, scales):
        from scipy.spatial import ConvexHull

        x, y = frame.to_numpy(data["x"]), frame.to_numpy(data["y"])
        hull = ConvexHull(
            np.column_stack([x, y]), qhull_options=self.params["qhull_options"]
        )
        idx = np.hstack([hull.vertices, hull.vertices[0]])

        return frame.frame_like(
            data,
            {
                "x": x[idx],
                "y": y[idx],
                "area": hull.area,
            },
        )
