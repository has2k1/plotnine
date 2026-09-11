from __future__ import annotations

import typing

import numpy as np

from .._utils import SIZE_FACTOR, to_rgba
from ..doctools import document
from ..exceptions import PlotnineError
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from typing import Any

    import numpy.typing as npt
    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea
    from matplotlib.path import Path

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


# key side (pt) at which a one-character pattern reads as a pattern on its own
HATCH_KEY_SIZE = 32
_VALID_HATCH = set(r"-+|/\xXoO.*")


def _add_hatch_overlays(ax, polygons, hatch, color, alpha, params, cls):
    """
    Draw hatch strokes over polygons that another collection already filled

    A matplotlib `Collection` takes one hatch pattern for all of its paths, so
    each distinct pattern needs a collection of its own. These carry no fill
    and no border: the caller's collection drew both, and drawing the border
    again would double its stroke and lose its linetype.
    """
    import matplotlib as mpl
    import pandas as pd

    # A fresh Series indexes by position, so the groups below can index into
    # `polygons`; object dtype keeps categorical hatch column from rejecting ""
    hatch = pd.Series(list(hatch), dtype=object).fillna("")
    if not hatch.ne("").any():
        return

    # A non-string reaches set_hatch intact and fails in the renderer, and an
    # unhashable one fails in the groupby below, so check before either.
    bad = next((h for h in hatch if not isinstance(h, str)), None)
    if bad is not None:
        raise PlotnineError(
            f"Cannot interpret hatch pattern {bad!r}. Hatch must be a string "
            "(e.g. '/', '//', 'xx', '.o'). If you mapped a variable to "
            "hatch, ensure it is a string column."
        )

    # matplotlib takes the hatch colour from the edge, and plotnine's default
    # `color` is None -- which would leave the strokes invisible. Fall back to
    # the colour the legend key ends up using.
    colors = to_rgba(
        pd.Series(list(color), dtype=object).fillna(
            mpl.rcParams["patch.edgecolor"]
        ),
        list(alpha),
    )

    for pattern, idx in hatch.groupby(hatch).groups.items():
        if not pattern:
            continue
        # matplotlib will allow some characters to fail silently (eg.: by
        # drawing an empty bar), so we raise here.
        invalid = set(pattern) - _VALID_HATCH
        if invalid:
            raise PlotnineError(
                f"Cannot interpret hatch pattern {pattern!r}: "
                f"{''.join(sorted(invalid))!r} is not a hatch character. "
                r"Valid characters are '-+|/\xXoO.*'."
            )
        idx = list(idx)
        overlay = cls(
            [polygons[i] for i in idx],
            facecolors="none",
            edgecolors=[colors[i] for i in idx],
            linewidths=0,
            zorder=params["zorder"],
            rasterized=params["raster"],
        )
        overlay.set_hatch(pattern)
        ax.add_collection(overlay)


@document
class geom_polygon(geom):
    """
    Polygon, a filled path

    {usage}

    Parameters
    ----------
    {common_parameters}

    Notes
    -----
    All paths in the same `group` aesthetic value make up a polygon.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Aesthetics Descriptions**

    `subgroup`

    :   Identify the rings within one `group`. The first ring forms the
        exterior; each later ring with the opposite winding direction
        forms a hole.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": None,
        "fill": "#333333",
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "y"}

    legend_key_size = staticmethod(geom_path.legend_key_size)

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, self.params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        from matplotlib.collections import PathCollection, PolyCollection

        # Polygon vertices omit the closing edge. Non-linear coordinates
        # must interpolate that edge with the others; otherwise a curved
        # boundary closes with a straight chord. Append each ring's first
        # vertex before transformation. Linear coordinates already close
        # the ring correctly.
        if not coord.is_linear:
            by = ["group", "subgroup"] if "subgroup" in data else "group"
            # A missing `subgroup` still identifies one ring. Preserve it
            # during grouping or its vertices disappear.
            indices = data.groupby(by, sort=False, dropna=False).indices
            order = np.concatenate(
                [np.append(idx, idx[0]) for idx in indices.values()]
            )
            data = data.iloc[order].reset_index(drop=True)

        data = coord.transform(data, panel_params, munch=True)
        data["linewidth"] = data["size"] * SIZE_FACTOR

        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        polygons = []
        facecolor = []
        edgecolor = []
        linestyle = []
        linewidth = []
        hatch = []
        alpha = []

        # Some stats may order the data in ways that prevent
        # objects from occluding other objects. We do not want
        # to undo that order.
        has_subgroups = "subgroup" in data
        grouper = data.groupby("group", sort=False)
        for group, df in grouper:
            fill = to_rgba(df["fill"].iloc[0], df["alpha"].iloc[0])
            if has_subgroups:
                # A missing `subgroup` still identifies one ring. A group
                # containing only that ring is a polygon without holes.
                rings = df.groupby("subgroup", sort=False, dropna=False)
                polygons.append(
                    compound_path(
                        [ring[["x", "y"]].to_numpy() for _, ring in rings]
                    )
                )
            else:
                polygons.append(tuple(zip(df["x"], df["y"])))
            facecolor.append("none" if fill is None else fill)
            edgecolor.append(df["color"].iloc[0] or "none")
            linestyle.append(df["linetype"].iloc[0])
            linewidth.append(df["linewidth"].iloc[0])
            hatch.append(df["hatch"].iloc[0] if "hatch" in df else None)
            alpha.append(df["alpha"].iloc[0])

        cls = PathCollection if has_subgroups else PolyCollection
        col = cls(
            polygons,
            facecolors=facecolor,
            edgecolors=edgecolor,
            linestyles=linestyle,
            linewidths=linewidth,
            zorder=params["zorder"],
            rasterized=params["raster"],
        )

        ax.add_collection(col)
        _add_hatch_overlays(
            ax,
            polygons,
            hatch,
            [e if e != "none" else None for e in edgecolor],
            alpha,
            params,
            cls,
        )

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a rectangle in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        from matplotlib.patches import Rectangle

        # We take into account that the linewidth
        # bestrides the boundary of the rectangle
        linewidth = data["size"] * SIZE_FACTOR
        linewidth = np.min([linewidth, da.width / 4, da.height / 4])

        if data["color"] is None:
            linewidth = 0

        facecolor = to_rgba(data["fill"], data["alpha"])
        if facecolor is None:
            facecolor = "none"

        # matplotlib tiles the hatch at a fixed physical size, so a key already
        # shows more strokes the bigger it is. Repeat the pattern only while
        # the key is too small to show it; a key of HATCH_KEY_SIZE or more
        # shows the pattern at the same density as the panel.
        hatch = data.get("hatch")
        if isinstance(hatch, str) and hatch:
            size = max(min(da.width, da.height), 1)
            reps = max(1, round(HATCH_KEY_SIZE / size))
            hatch = "".join(c * reps for c in hatch)
        else:
            hatch = None

        rect = Rectangle(
            (0 + linewidth / 2, 0 + linewidth / 2),
            width=da.width - linewidth,
            height=da.height - linewidth,
            linewidth=linewidth,
            linestyle=data["linetype"],
            facecolor=facecolor,
            edgecolor=data["color"],
            hatch=hatch,
            capstyle="projecting",
        )
        da.add_artist(rect)
        return da


def compound_path(rings: list[npt.NDArray[Any]]) -> Path:
    """
    Combine polygon rings into one path

    Under the non-zero winding rule, a ring whose direction opposes its
    enclosing ring forms a hole.
    """
    from matplotlib.path import Path

    vertices = np.concatenate([np.vstack([r, r[:1]]) for r in rings])
    codes = np.concatenate(
        [
            [Path.MOVETO, *[Path.LINETO] * (len(r) - 1), Path.CLOSEPOLY]
            for r in rings
        ]
    )
    return Path(vertices, codes)
