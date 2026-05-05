# Geoms

Geometric objects (geoms) are the visual marks placed on a plot. Each geom
represents data using different shapes: points, lines, bars, etc.

## Reading Order

| Task                        | Read in order                                                       |
|-----------------------------|---------------------------------------------------------------------|
| Pick a geom                 | Geom Quick-Reference → `api/geom_<name>.md`                          |
| Compose a geom with a stat  | Geom Quick-Reference → `statistical-layers.md`                       |
| Combine multiple geoms      | Composition Examples below                                          |

## Geom Quick-Reference

| Geom | Typical aes | Default stat | Common params |
|------|------------|--------------|---------------|
| `geom_point` | x, y, color, size, shape, alpha | `identity` | `size`, `alpha` |
| `geom_jitter` | x, y, color, size, shape | `identity` | `width`, `height` |
| `geom_line` | x, y, color, linetype, group | `identity` | `size` |
| `geom_step` | x, y, color, linetype | `identity` | `direction` |
| `geom_bar` | x, fill, color | `count` | `width`, `position` |
| `geom_col` | x, y, fill, color | `identity` | `width`, `position` |
| `geom_histogram` | x, fill, color | `bin` | `bins`, `binwidth` |
| `geom_density` | x, fill, color, linetype | `density` | `alpha` |
| `geom_boxplot` | x, y, fill, color | `boxplot` | `width`, `outlier_shape` |
| `geom_violin` | x, y, fill, color | `ydensity` | `scale`, `draw_quantiles` |
| `geom_area` | x, y, fill, alpha | `identity` | — |
| `geom_ribbon` | x, ymin, ymax, fill, alpha | `identity` | — |
| `geom_tile` | x, y, fill | `identity` | `width`, `height` |
| `geom_segment` | x, y, xend, yend, color | `identity` | `arrow` |
| `geom_rug` | x, y, color | `identity` | `sides`, `length` |
| `geom_smooth` | x, y, color | `smooth` | `method`, `se` |
| `geom_text` | x, y, label, color, size | `identity` | `nudge_x`, `nudge_y` |

### How geoms and stats share parameters

The "Common params" column above lists parameters that belong to the
geom's **default stat**, not the geom itself. Every geom forwards its
`**kwargs` to its paired stat, so `geom_histogram(binwidth=0.5)` is
passing `binwidth` through to `stat_bin`, and
`geom_smooth(method="lm", se=False)` is passing both kwargs through
to `stat_smooth`.

Consequences:

- A geom's own parameters are `mapping`, `data`, `stat`, `position`,
  `na_rm`, plus a small number of geom-specific options.
- Parameters like `binwidth`, `bins`, `method`, `span`, `width`,
  `scale`, `direction` live on the stat.
- Pairing a geom with a non-default stat
  (e.g. `geom_bar(stat="identity")`) changes which kwargs are
  accepted — the stat's, not the geom's.

See [statistical-layers.md](statistical-layers.md) for stat-specific
details.

## Quick one-liners

Each geom below is a complete layer. Combine with the minimal
`ggplot() + aes() + labs()` structure shown in SKILL.md Essentials.

```python
# Scatter
geom_point()

# Bar chart (counts)
geom_bar()                              # x only, counts rows

# Bar chart (pre-computed values)
geom_col()                              # x and y required

# Line chart
geom_line()                             # sort data by x first

# Histogram
geom_histogram(binwidth=0.5)

# Box plot
geom_boxplot()                          # x (categorical) and y (continuous)
```

Parameter reference and single-geom examples live in
`api/<geom>.md` — open the file named after the geom you're using.

## Composition Examples

Cross-cutting patterns that combine two or more geoms into a single
plot. For patterns that use only one geom, see that geom's file under
`api/`.

### Violin + jitter

Layering `geom_violin` with `geom_jitter` shows both distribution
shape and individual observations.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_violin()
    + geom_jitter(width=0.15, alpha=0.4, size=1)
    + labs(x="Vehicle Class", y="Highway MPG", title="Highway MPG: Violin + Points")
)
```

### Confidence band (ribbon + line)

`geom_ribbon` requires `ymin` and `ymax` aesthetics. Pair it with
`geom_line` for a fit-plus-band visual.

```python
from plotnine import *
import pandas as pd
import numpy as np

x = np.arange(0, 10, 0.5)
y = np.sin(x)
df = pd.DataFrame({"x": x, "y": y, "ymin": y - 0.3, "ymax": y + 0.3})

(
    ggplot(df, aes(x="x", y="y"))
    + geom_ribbon(aes(ymin="ymin", ymax="ymax"), alpha=0.3)
    + geom_line()
    + labs(x="X", y="Y", title="Line with Confidence Band")
)
```

### Lollipop chart (point + segment)

Drop a segment from each point to the x-axis for a lollipop effect.

```python
from plotnine import *
from plotnine.data import economics

subset = economics.iloc[::60].copy()

(
    ggplot(subset, aes(x="date", y="unemploy"))
    + geom_point()
    + geom_segment(aes(xend="date", yend=0), alpha=0.4)
    + labs(x="Date", y="Unemployed (thousands)", title="Lollipop Chart of Unemployment")
)
```

## Common Pitfalls

- **`geom_bar` vs `geom_col`**: `geom_bar` counts rows (no `y` aes);
  `geom_col` uses pre-computed `y` values. Using `geom_bar` with a `y`
  aesthetic requires `stat="identity"`, but prefer `geom_col` instead.

- **`color` inside vs outside `aes()`**: `aes(color="species")` maps a
  variable; `color="blue"` sets a fixed value. Putting a fixed color inside
  `aes()` creates a legend entry for a literal string. See
  [aesthetics-and-scales.md](aesthetics-and-scales.md) for details.

- **`bins` vs `binwidth`**: Use one or the other with `geom_histogram`, not
  both. `bins=30` (default) sets the number of bins; `binwidth=0.1` sets the
  width of each bin.

- **Unsorted data with `geom_line`**: `geom_line` connects points in x-order.
  If your data is not sorted by x, the line will zigzag. Sort before plotting:
  `df.sort_values("x")`.

- **Overplotting**: With many data points, use `alpha` transparency,
  `geom_jitter`, `geom_bin2d`, or `geom_density_2d` instead of `geom_point`.

## See Also

- `api/geom_<name>.md` — parameter reference for each geom
- [aesthetics-and-scales.md](aesthetics-and-scales.md) — mapping
  variables to geom aesthetics
- [statistical-layers.md](statistical-layers.md) — smoothers,
  stat summaries, and position adjustments
- [facets.md](facets.md) — splitting a geom across small multiples
- [labels-and-annotations.md](labels-and-annotations.md) — adding
  text labels to geoms
