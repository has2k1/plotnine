import pandas as pd
import numpy as np

from ..coords import coord_flip
from ..scales.scale import scale_discrete
from .geom import geom
from .geom_rect import geom_rect
from .annotate import annotate


class annotation_stripes(annotate):
    """
    Alternating stripes, centered around each label.

    Useful as a background for geom_jitter.

    {usage}
    plot += annotation_stripes(fill=['red', 'blue'], alpha=0.3)

    Parameters
    ----------
    fills - list of colors to alternate through.
    Default: ["#AAAAAA", "#CCCCCC"]

    direction: 'vertical' or 'horizontal'
    orientation of the stripes

    {common_parameters}
    """

    def __init__(self, **kwargs):
        if 'direction' in kwargs:
            allowed = ('vertical', 'horizontal')
            if ((not isinstance(kwargs['direction'], str))
                    or (kwargs['direction'] not in allowed)):
                raise ValueError("direction must be one of %s" % (allowed, ))
        self._annotation_geom = _geom_annotation_stripes(
            **kwargs)


class _geom_annotation_stripes(geom):

    DEFAULT_AES = {}
    REQUIRED_AES = set()
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "color": None,
        "fills": ["#AAAAAA", "#CCCCCC"],
        "linetype": "solid",
        "size": 0,
        "alpha": 0.5,
        'direction': 'vertical',
        'extend': (0, 1),
    }
    legend_geom = "polygon"

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        is_coord_flip = isinstance(coord, coord_flip)
        direction = params.get('direction', 'vertical')
        if direction == 'vertical':
            scale = getattr(panel_params["scales"], "x")
            if is_coord_flip:
                prefix, other_prefix = "y_", "x_"
            else:
                prefix, other_prefix = "x_", "y_"
        else:
            scale = getattr(panel_params["scales"], "y")
            if is_coord_flip:
                prefix, other_prefix = "x_", "y_"
            else:
                prefix, other_prefix = "y_", "x_"

        is_scale_discrete = isinstance(scale, scale_discrete)
        fills = list(params["fills"])
        count = len(panel_params[prefix + "labels"])
        if is_scale_discrete:
            step_size = 1
            left = np.arange(0, count, 1) + 0.5
        else:
            step_size = (
                panel_params[prefix + "major"][-1] -
                panel_params[prefix + "major"][0]
            ) / (count - 1)
            left = panel_params[prefix + "major"] - step_size / 2
        right = left + step_size
        left[0] = panel_params[prefix + "range"][0]
        right[-1] = panel_params[prefix + "range"][1]
        data = pd.DataFrame(
            {
                "xmin": left,
                "xmax": right,
                "ymin": panel_params[other_prefix + "range"][0],
                "ymax": panel_params[other_prefix + "range"][1],
                "fill": (fills * len(left))[: len(left)],
                "size": params["size"],
                "linetype": params["linetype"],
                "alpha": params["alpha"],
                "color": "#000000",
            }
        )
        if (direction == 'horizontal'):
            data = data.rename(
                columns={"xmin": "ymin", "xmax": "ymax",
                         "ymin": "xmin", "ymax": "xmax"}
            )
        return geom_rect.draw_group(data, panel_params, coord, ax, **params)
