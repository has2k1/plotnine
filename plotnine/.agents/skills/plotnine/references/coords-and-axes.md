# Coordinates and Axes

Coordinate systems control how data coordinates map to the 2D plane
of the plot. They affect axis limits, aspect ratio, and coordinate
transformations. Per-coord parameter surface and single-coord
examples live at `api/coord_<name>.md`.

This file covers two cross-cutting topics: the difference between
limits set on a scale (drops data) versus on a coord (zooms), and the
lack of polar coordinates in plotnine.

## Reading Order

| Task                              | Read in order                                                       |
|-----------------------------------|---------------------------------------------------------------------|
| Pick a coord                      | `api/coord_<name>.md`                                               |
| Zoom in without affecting stats   | `lims() vs coord_cartesian()` below → `api/coord_cartesian.md`      |
| Make a polar plot                 | No coord_polar below (use workarounds)                              |

## lims() vs coord_cartesian()

These two approaches to setting axis limits behave differently:

| Approach                            | Behavior                           | Affects stats? |
|-------------------------------------|------------------------------------|----------------|
| `lims(x=(a, b))`                    | **Removes** data outside range     | Yes            |
| `scale_x_continuous(limits=(a, b))` | **Removes** data outside range     | Yes            |
| `coord_cartesian(xlim=(a, b))`      | **Zooms** without removing data    | No             |

### Data removal vs zooming

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + lims(x=(3, 6))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="lims() Removes Data Outside Range")
)
```

Compare with `coord_cartesian`, which preserves all data for the
smooth fit:

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + coord_cartesian(xlim=(3, 6))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="coord_cartesian() Zooms (Data Preserved)")
)
```

## No coord_polar

plotnine does not support polar coordinates. There is no
`coord_polar()` function. For pie charts or radar charts, consider
alternative representations:

- Pie chart → stacked or dodged bar chart
- Radar chart → parallel coordinates or faceted bar chart

## Common Pitfalls

- **`lims()` removes data, affecting stats**: Using `lims(y=(0, 40))` drops
  rows where y > 40 before computing `geom_smooth` or `stat_summary`. This
  changes the fitted line or summary statistics. Use `coord_cartesian(ylim=...)`
  to zoom without altering computations.

- **`coord_cartesian()` only zooms**: It does not filter data or change the
  underlying data range. Points outside the view still participate in all
  statistical computations.

- **`coord_flip` with discrete x**: When flipping a bar chart, the variable
  mapped to `x` appears on the y-axis visually, but you still define it as
  `aes(x=...)`. Do not swap x and y in the aesthetic mapping.

- **`coord_fixed` distorts when data ranges differ**: If x ranges from 0-100
  and y from 0-10, `coord_fixed(ratio=1)` creates an extremely wide plot. Use
  a different ratio or let plotnine choose automatically.

## See Also

- `api/coord_<name>.md` — parameter reference and single-coord examples
- [aesthetics-and-scales.md](aesthetics-and-scales.md) — position
  scales (`scale_x_continuous`, `scale_y_log10`, etc.)
- [facets.md](facets.md) — `scales="free"` to let each panel pick
  its own coordinate range
- [maps.md](maps.md) — `coord_fixed()` is essential for geographic plots
