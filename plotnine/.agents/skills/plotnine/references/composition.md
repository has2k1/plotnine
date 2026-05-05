# Composition

Composition arranges multiple independent plots into a single figure using
operators. Requires plotnine 0.15+.

## Operators

| Operator | Class | Description |
|----------|-------|-------------|
| `\|` | `Beside` | Side by side (columns) |
| `/` | `Stack` | Vertical stacking (rows) |
| `-` | `Beside` | Side by side at same nesting level |
| `&` | — | Add layer/theme to **all** plots |
| `*` | — | Add layer/theme to **top-level** plots |
| `+` | — | Add layer/theme to **last** plot in composition |

Note: `+` on a composition adds to the last plot (e.g., adding a theme or
geom). To compose plots side by side, use `|`; to stack vertically, use `/`.

## Side by Side

The `|` operator places plots in columns using `Beside`.

```python
from plotnine import *
from plotnine.data import mpg

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Vehicle Class", y="Count", title="Bar Chart")
)

p1 | p2
```

### Three plots side by side

Chaining `|` adds more columns to the same `Beside` composition.

```python
from plotnine import *
from plotnine.data import mpg

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Vehicle Class", y="Count", title="Bars")
)

p3 = (
    ggplot(mpg, aes(x="hwy"))
    + geom_histogram(binwidth=2, fill="coral")
    + labs(x="Highway MPG", y="Count", title="Histogram")
)

p1 | p2 | p3
```

## Vertical Stacking

The `/` operator places plots in rows using `Stack`.

```python
from plotnine import *
from plotnine.data import mpg, economics

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(economics, aes(x="date", y="unemploy"))
    + geom_line()
    + labs(x="Date", y="Unemployed (thousands)", title="Unemployment")
)

p1 / p2
```

## Nesting

Combine `|` and `/` operators to create complex layouts. Use parentheses to
control nesting.

### 2x2 grid with nesting

```python
from plotnine import *
from plotnine.data import mpg

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Class", y="Count", title="Bars")
)

p3 = (
    ggplot(mpg, aes(x="hwy"))
    + geom_histogram(binwidth=2, fill="coral")
    + labs(x="Highway MPG", y="Count", title="Histogram")
)

p4 = (
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_boxplot()
    + labs(x="Class", y="Highway MPG", title="Boxplot")
)

(p1 | p2) / (p3 | p4)
```

### Asymmetric layout

```python
from plotnine import *
from plotnine.data import mpg, penguins

p_wide = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Full Width")
)

p_left = (
    ggplot(penguins.dropna(), aes(x="species", fill="species"))
    + geom_bar()
    + labs(x="Species", y="Count", fill="Species", title="Left Panel")
)

p_right = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Class", y="Count", title="Right Panel")
)

p_wide / (p_left | p_right)
```

## plot_spacer

Inserts a blank placeholder into the composition. Useful for controlling layout
when you need an empty cell.

```python
from plotnine import *
from plotnine.data import mpg
from plotnine.composition import plot_spacer

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Plot 1")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Class", y="Count", title="Plot 2")
)

p1 | plot_spacer() | p2
```

## Modifying All Plots

The `&` operator applies a layer, theme, or scale to every plot in the
composition. The `*` operator applies only to top-level plots (not nested
sub-compositions).

### Applying a theme to all plots

```python
from plotnine import *
from plotnine.data import mpg

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Class", y="Count", title="Bar Chart")
)

(p1 | p2) & theme_minimal()
```

### Adding a layer to the last plot only

The `+` operator on a composition adds to the last plot, not to all plots.

```python
from plotnine import *
from plotnine.data import mpg

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar()
    + labs(x="Class", y="Count", title="Bar Chart")
)

# theme_bw is added only to p2 (the last plot)
(p1 | p2) + theme_bw()
```

## Saving Compositions

Compositions have their own `.save()` method with a simpler signature than
`ggplot.save()`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `filename` | — | File path or `BytesIO` object |
| `format` | `None` | Image format (inferred from extension) |
| `dpi` | `None` | DPI for raster formats |

Note: The composition `.save()` does not accept `width`, `height`, or `units`.
Control figure size via `theme(figure_size=(W, H))` applied with `&`.

```python
from plotnine import *
from plotnine.data import mpg

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + labs(x="Displacement (L)", y="Highway MPG", title="Scatter")
)

p2 = (
    ggplot(mpg, aes(x="class"))
    + geom_bar(fill="steelblue")
    + labs(x="Class", y="Count", title="Bar Chart")
)

comp = (p1 | p2) & theme(figure_size=(10, 4))
comp.save("composition.png", dpi=300)
```

## Limitations

- **No inset plots**: plotnine does not support placing a small plot inside a
  larger one. Use separate panels or facets instead.
- **Shared legends**: Compositions do not automatically merge duplicate legends.
  Each plot renders its own legend independently.
- **No width/height control per panel**: Panel sizes within a composition are
  determined automatically. There is no way to set relative widths or heights
  of individual panels.

## Common Pitfalls

- **`|` is side-by-side, not vertical**: `p1 | p2` places plots in columns.
  For vertical stacking, use `p1 / p2`.

- **`+` adds to last plot, not all**: On a composition, `(p1 | p2) + theme_bw()`
  applies `theme_bw` only to `p2`. Use `&` to apply to all plots.

- **Operator precedence**: Python's `|` has lower precedence than `/`, and
  both are lower than `+`. Use parentheses to ensure the intended grouping:
  `(p1 | p2) / (p3 | p4)`.

- **Composition `.save()` ignores width/height**: Unlike `ggplot.save()`,
  the composition `.save()` does not accept `width` or `height`. Set the
  figure size via `theme(figure_size=...)` applied with `&`.

- **Scales don't share across composed plots**: Each plot has its own
  axis range. To make two plots share a y-scale, apply
  `scale_y_continuous(limits=(lo, hi))` (or `coord_cartesian(ylim=...)`)
  to both. There is no auto-sync — a value that clips in one plot
  won't propagate to its neighbour.

- **Duplicate legends from same-variable mappings**: If two composed
  plots both map the same variable to `color`, the composition
  renders two identical legends side by side; plotnine does not
  auto-merge them (see Limitations). Workaround: suppress the
  duplicate with `theme(legend_position="none")` on one plot, or
  restructure as a single faceted plot.

- **Stacked plots don't auto-align panels**: `p1 / p2` stacks panels
  but doesn't constrain panel widths to match. If `p1` has wider
  y-tick labels than `p2`, the plotting areas offset horizontally.
  Normalize tick label widths (pad with leading spaces, or fix
  `limits` so both plots render the same tick format) to align.

## See Also

- [themes-and-styling.md](themes-and-styling.md) — `figure_size`
  applied with `&` sets composition dimensions
- [saving-and-export.md](saving-and-export.md) — composition `.save()`
  differs from `ggplot.save()` (no `width`/`height`)
