# Themes and Styling

Themes control the non-data appearance of a plot: backgrounds, gridlines, fonts,
and legend placement. plotnine provides built-in themes and a flexible `theme()`
system for customization.

## Reading Order

| Task                             | Read in order                                                      |
|----------------------------------|--------------------------------------------------------------------|
| Pick a built-in theme            | Built-In Themes                                                    |
| Customize specific elements      | Built-In Themes → theme() Element System → Common Customizations   |
| Build a reusable theme           | theme() Element System → Reusable Custom Theme                     |
| Layer multiple tweaks additively | theme() Element System → Cumulative Theme Additions                |

## Built-In Themes

plotnine includes 14 built-in themes. By default, plotnine uses `theme_gray`.

| Theme | Description |
|-------|-------------|
| `theme_gray()` | Default gray background with white gridlines |
| `theme_grey()` | Alias for `theme_gray` |
| `theme_bw()` | White background with thin gray gridlines |
| `theme_linedraw()` | White background with black border and gridlines |
| `theme_light()` | Light gray axes and gridlines |
| `theme_dark()` | Dark gray background |
| `theme_minimal()` | Minimal: no background, no border, light gridlines |
| `theme_classic()` | Classic: only x and y axis lines, no gridlines |
| `theme_void()` | Completely blank (useful for maps or diagrams) |
| `theme_538()` | FiveThirtyEight style |
| `theme_tufte()` | Edward Tufte's minimal ink style |
| `theme_seaborn()` | Seaborn-inspired defaults |
| `theme_matplotlib()` | matplotlib default style |
| `theme_xkcd()` | XKCD comic style |

### Applying a theme

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + theme_minimal()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Scatter with Minimal Theme")
)
```

### Comparing themes

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + theme_bw()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Scatter with BW Theme")
)
```

## theme() Element System

The `theme()` function customizes individual plot elements. Each element is
controlled by one of four element types:

| Element function | Controls | Key parameters |
|-----------------|----------|----------------|
| `element_text()` | Text elements | `size`, `color`, `family`, `weight`, `rotation` |
| `element_line()` | Lines and ticks | `color`, `size`, `linetype` |
| `element_rect()` | Rectangles (backgrounds, borders) | `fill`, `color`, `size` |
| `element_blank()` | Remove an element entirely | — |

### theme() Parameter Reference

| Parameter | Element type | What it controls |
|-----------|-------------|------------------|
| `plot_title` | `element_text` | Plot title |
| `plot_subtitle` | `element_text` | Plot subtitle |
| `axis_title` | `element_text` | Both axis titles |
| `axis_title_x` | `element_text` | X-axis title |
| `axis_title_y` | `element_text` | Y-axis title |
| `axis_text` | `element_text` | Both axis tick labels |
| `axis_text_x` | `element_text` | X-axis tick labels |
| `axis_text_y` | `element_text` | Y-axis tick labels |
| `axis_ticks` | `element_line` | Axis tick marks |
| `axis_line` | `element_line` | Axis lines |
| `legend_title` | `element_text` | Legend title |
| `legend_text` | `element_text` | Legend labels |
| `legend_position` | string/tuple | Legend placement |
| `legend_direction` | string | `"horizontal"` or `"vertical"` |
| `panel_background` | `element_rect` | Plot panel background |
| `panel_grid_major` | `element_line` | Major gridlines |
| `panel_grid_minor` | `element_line` | Minor gridlines |
| `panel_border` | `element_rect` | Panel border |
| `strip_background` | `element_rect` | Facet strip background |
| `strip_text` | `element_text` | Facet strip text |
| `figure_size` | tuple | Figure width and height in inches |

## Common Customizations

### Rotate x-axis labels

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="manufacturer"))
    + geom_bar()
    + theme(axis_text_x=element_text(rotation=45, ha="right"))
    + labs(x="Manufacturer", y="Count", title="Cars by Manufacturer")
)
```

### Adjust font sizes

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species"))
    + geom_point()
    + theme(
        plot_title=element_text(size=16, weight="bold"),
        axis_title=element_text(size=12),
        axis_text=element_text(size=10),
    )
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguin Bills", color="Species")
)
```

### Move or remove the legend

```python
from plotnine import *
from plotnine.data import mpg

# Legend at the bottom
(
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(cyl)"))
    + geom_point()
    + theme(legend_position="bottom")
    + labs(x="Displacement (L)", y="Highway MPG", title="Legend at Bottom", color="Cylinders")
)
```

```python
from plotnine import *
from plotnine.data import mpg

# Remove legend entirely
(
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(cyl)"))
    + geom_point()
    + theme(legend_position="none")
    + labs(x="Displacement (L)", y="Highway MPG", title="No Legend")
)
```

### Remove gridlines

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(1000, random_state=42), aes(x="carat", y="price"))
    + geom_point(alpha=0.3, size=1)
    + theme_minimal()
    + theme(
        panel_grid_minor=element_blank(),
        panel_grid_major=element_line(color="#EEEEEE"),
    )
    + labs(x="Carat", y="Price (USD)", title="Minimal Grid")
)
```

### Set figure size

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + theme(figure_size=(8, 4))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Wide Figure")
)
```

## Reusable Custom Theme

Define a function that returns a theme combination for consistent styling
across plots.

```python
from plotnine import *
from plotnine.data import penguins


def theme_publication():
    return (
        theme_minimal()
        + theme(
            plot_title=element_text(size=14, weight="bold"),
            axis_title=element_text(size=11),
            axis_text=element_text(size=10),
            legend_position="bottom",
            panel_grid_minor=element_blank(),
            figure_size=(7, 5),
        )
    )


(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species"))
    + geom_point()
    + theme_publication()
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Publication-Ready Scatter", color="Species")
)
```

## Cumulative Theme Additions

Themes are additive. A built-in theme sets all elements, then `theme()`
overrides specific ones. Multiple `theme()` calls accumulate.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_boxplot()
    + theme_bw()  # sets base look
    + theme(axis_text_x=element_text(rotation=45, ha="right"))  # override one element
    + theme(legend_position="none")  # override another element
    + labs(x="Vehicle Class", y="Highway MPG", title="Cumulative Theme Overrides")
)
```

## Common Pitfalls

- **Underscores, not dots**: plotnine uses `axis_text_x`, not `axis.text.x`
  (the R/ggplot2 convention). Use underscores throughout.

- **`rotation`, not `angle`**: `element_text(rotation=45)` is correct.
  `angle` is the ggplot2 R parameter name and does not work in plotnine.

- **`legend_position="none"`, not `False`**: To hide the legend, pass the
  string `"none"`. Valid positions: `"right"`, `"left"`, `"top"`, `"bottom"`,
  `"none"`, or a `(x, y)` tuple for precise placement.

- **Cumulative theme additions**: Calling `theme()` multiple times does not
  reset previous overrides. Each `theme()` call adds to the accumulation.
  To reset, apply a fresh built-in theme first.

- **`ha` for horizontal alignment**: When rotating x-axis labels, set
  `ha="right"` in `element_text()` to anchor rotated text correctly.

- **`element_blank()` wipes the whole element**:
  `theme(axis_title=element_blank())` removes *both* x and y axis
  titles, not just one. To blank a single axis, target
  `axis_title_x` or `axis_title_y` directly.

- **Theme element inheritance**: Top-level elements propagate to
  children. `theme(text=element_text(size=12))` sets the font size
  for all text (axis text, axis titles, legend text, strip text,
  etc.) unless a child element overrides it. Child overrides always
  win — order in the `+` chain does not change that.

- **`figure_size` vs `save(width, height)`**: `theme(figure_size=(W, H))`
  is the default plot dimension (in inches). Passing `width=` /
  `height=` to `ggplot.save()` overrides that default for the saved
  output. The theme value applies to in-notebook display; the save
  argument wins at export time.

- **Panel vs plot background**: `panel_background` fills the plotting
  area inside the axes. `plot_background` fills the whole figure
  (around the title, axis labels, and legend). To fully recolor the
  plot, set both.

## See Also

- [aesthetics-and-scales.md](aesthetics-and-scales.md) — legends,
  guides, and scale customization (theme controls their appearance)
- [color-and-accessibility.md](color-and-accessibility.md) —
  palettes that pair with theme choices
- [aesthetic-specification.md](aesthetic-specification.md) — literal
  values for theme element properties (colors, fonts, sizes)
