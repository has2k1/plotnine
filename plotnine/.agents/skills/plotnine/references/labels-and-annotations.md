# Labels and Annotations

Labels provide context — titles, axis names, legend headings. Annotations add
non-data-driven marks — text callouts, shaded regions, reference lines.

## labs()

`labs()` sets or overrides labels for any aesthetic, plus title, subtitle,
caption, footer, and tag.

| Parameter | Description |
|-----------|-------------|
| `title` | Plot title (top) |
| `subtitle` | Subtitle below title |
| `caption` | Caption (bottom-right) |
| `footer` | Footer (bottom, plotnine 0.16+) |
| `tag` | Panel tag (e.g., "A", "B") |
| `x`, `y` | Axis labels |
| `color` / `colour` | Color legend title |
| `fill` | Fill legend title |
| `size` | Size legend title |
| `shape` | Shape legend title |
| `alpha` | Alpha legend title |
| `linetype` | Linetype legend title |

### Full labels example

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(cyl)"))
    + geom_point(alpha=0.6)
    + labs(
        x="Engine Displacement (L)",
        y="Highway MPG",
        color="Cylinders",
        title="Fuel Efficiency by Engine Size",
        subtitle="Highway mileage decreases with displacement",
        caption="Source: EPA fuel economy data",
    )
)
```

## Shorthand Functions

| Function | Equivalent |
|----------|------------|
| `ggtitle("Title")` | `labs(title="Title")` |
| `ggtitle("Title", "Subtitle")` | `labs(title="Title", subtitle="Subtitle")` |
| `xlab("Label")` | `labs(x="Label")` |
| `ylab("Label")` | `labs(y="Label")` |

### Using shorthand

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + ggtitle("Fuel Efficiency", "Highway mileage vs engine displacement")
    + xlab("Engine Displacement (L)")
    + ylab("Highway MPG")
)
```

## annotate()

`annotate()` adds a single geom that is not mapped to data. It operates in
data coordinates but does not iterate over data rows.

| Parameter | Description |
|-----------|-------------|
| `geom` | Geom name as string (e.g., `"text"`, `"rect"`, `"segment"`) |
| `x`, `y` | Position in data coordinates |
| `xmin`, `xmax`, `ymin`, `ymax` | For rect, used instead of x/y |
| `xend`, `yend` | For segment end point |
| `**kwargs` | Passed to the geom (color, size, alpha, etc.) |

### Text annotation

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + annotate("text", x=6, y=40, label="Outlier region", size=10, color="red")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Annotated Scatter Plot")
)
```

### Rectangle highlight

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + annotate("rect", xmin=5, xmax=7, ymin=30, ymax=45, alpha=0.1, fill="blue")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Highlighted Region")
)
```

### Segment annotation

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + annotate("segment", x=5, y=40, xend=6.5, yend=25, color="red", size=1)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Segment Callout")
)
```

## geom_text and geom_label

Unlike `annotate()`, these geoms are data-driven — they map data columns to
label positions and content.

| Parameter | Description |
|-----------|-------------|
| `nudge_x`, `nudge_y` | Offset labels from point position |
| `adjust_text` | Dict of parameters for repelling overlaps (uses adjustText) |
| `format_string` | Python format string applied to label values |
| `ha` | Horizontal alignment (`"left"`, `"center"`, `"right"`) |
| `va` | Vertical alignment (`"top"`, `"center"`, `"bottom"`) |

`geom_label` inherits all `geom_text` params and adds a background box.

### Data-driven labels with nudge

```python
from plotnine import *
from plotnine.data import mpg
import pandas as pd

avg_hwy = mpg.groupby("class", as_index=False).agg(mean_hwy=("hwy", "mean"))

(
    ggplot(avg_hwy, aes(x="class", y="mean_hwy"))
    + geom_col(fill="steelblue")
    + geom_text(aes(label="mean_hwy"), format_string="{:.1f}", nudge_y=1, size=8)
    + labs(x="Vehicle Class", y="Mean Highway MPG", title="Bar Labels with geom_text")
)
```

### geom_label with background box

```python
from plotnine import *
from plotnine.data import mpg
import pandas as pd

top_cars = mpg.nlargest(5, "hwy")[["manufacturer", "model", "displ", "hwy"]].copy()
top_cars["name"] = top_cars["manufacturer"] + " " + top_cars["model"]

(
    ggplot(top_cars, aes(x="displ", y="hwy"))
    + geom_point(size=3)
    + geom_label(aes(label="name"), nudge_y=1, size=7)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Top 5 Most Efficient Cars")
)
```

## Arrow Annotations

Use `annotate("segment", ...)` with the `arrow()` function for callout arrows.

```python
from plotnine import *
from plotnine.data import economics

(
    ggplot(economics, aes(x="date", y="unemploy"))
    + geom_line()
    + annotate("segment", x="2009-01-01", y=14000, xend="2009-10-01", yend=15000, arrow=arrow(length=0.15), color="red")
    + annotate("text", x="2007-06-01", y=14000, label="2009 peak", size=9, color="red")
    + labs(x="Date", y="Unemployed (thousands)", title="US Unemployment with Arrow Callout")
)
```

## Reference Lines

`geom_hline`, `geom_vline`, and `geom_abline` draw lines across the full plot
area. These are not mapped to data rows.

| Geom | Required aes | Description |
|------|-------------|-------------|
| `geom_hline` | `yintercept` | Horizontal line |
| `geom_vline` | `xintercept` | Vertical line |
| `geom_abline` | `slope`, `intercept` | Diagonal line |

### Horizontal and vertical reference lines

```python
from plotnine import *
from plotnine.data import mpg

mean_hwy = mpg["hwy"].mean()

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_hline(yintercept=mean_hwy, linetype="dashed", color="red")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Scatter with Mean Reference Line")
)
```

### Diagonal reference line

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="flipper_length_mm"))
    + geom_point(alpha=0.5)
    + geom_abline(slope=3, intercept=50, linetype="dashed", color="grey")
    + labs(x="Bill Length (mm)", y="Flipper Length (mm)", title="Penguin Measurements with Reference Line")
)
```

## Common Pitfalls

- **`annotate()` vs `geom_text()`**: `annotate()` places fixed text at
  specified coordinates — it does not iterate over data rows. `geom_text()`
  maps data columns to labels and draws one label per row. Use `annotate()`
  for callout labels; use `geom_text()` for data-driven labels.

- **Missing `label` aesthetic in `geom_text`**: `geom_text` requires
  `aes(label="column_name")`. Omitting it raises an error.

- **Forgetting to update `labs()` after changing aesthetics**: When you change
  `aes(color=...)` to a different variable, the legend title reverts to the
  raw column name. Always update the corresponding `labs()` parameter.

- **`annotate("text")` size vs `geom_text` size**: Both use `size` in points,
  but the visual size may differ because `annotate()` does not inherit the
  default theme text size. Set `size` explicitly for consistency.

## See Also

- [geoms.md](geoms.md) — the geoms carrying these annotations
- [aesthetics-and-scales.md](aesthetics-and-scales.md) — setting
  `name=` on a scale (alternative to `labs(aes=...)`)
- [themes-and-styling.md](themes-and-styling.md) — styling title,
  subtitle, caption, and annotation text
