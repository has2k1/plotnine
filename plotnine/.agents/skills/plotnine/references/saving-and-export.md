# Saving and Export

plotnine plots are saved via `ggplot.save()`. The method wraps matplotlib's
`savefig` with plotnine-specific defaults for size and resolution.

## ggplot.save()

| Parameter | Default | Description |
|-----------|---------|-------------|
| `filename` | — | File path or `BytesIO` object |
| `format` | `None` | Image format (inferred from extension if `None`) |
| `path` | `None` | Directory prefix for `filename` |
| `width` | `None` | Figure width (uses theme default if `None`) |
| `height` | `None` | Figure height (uses theme default if `None`) |
| `units` | `"in"` | Size units: `"in"`, `"cm"`, `"mm"` |
| `dpi` | `None` | Resolution for raster formats (uses theme default if `None`) |
| `limitsize` | `True` | Prevent accidentally large figures (>25 inches) |
| `verbose` | `False` | Print file info after saving |
| `**kwargs` | — | Passed to matplotlib's `savefig` |

### Basic save

```python
from plotnine import *
from plotnine.data import mpg

p = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency")
    + theme(
        figure_size=(6, 4),
        dpi=300,
    )
)

p.save("mpg_scatter.png")
```

In `theme`, the `figure_size` i.e. (width, height) is always in inches.

### Save with centimeter units

```python
from plotnine import *
from plotnine.data import mpg

p = (
    ggplot(mpg, aes(x="class"))
    + geom_bar()
    + labs(x="Vehicle Class", y="Count", title="Cars by Class")
)

p.save("mpg_bar.png", width=15, height=10, units="cm", dpi=300)
```

## Supported Formats

| Format | Extension | Type | Notes |
|--------|-----------|------|-------|
| PNG | `.png` | Raster | Default for web; supports transparency |
| PDF | `.pdf` | Vector | Best for print; text remains selectable |
| SVG | `.svg` | Vector | Good for web; editable in vector tools |
| EPS | `.eps` | Vector | Legacy print workflows |
| JPEG | `.jpg` | Raster | Lossy compression; no transparency |
| TIFF | `.tiff` | Raster | Lossless; large files |

The format is auto-detected from the file extension. Override with the
`format` parameter when saving to a `BytesIO` buffer or non-standard
extension.

## Recommended Sizes

| Use Case | Width | Height | DPI | Notes |
|----------|-------|--------|-----|-------|
| Web / README | 6 | 4 | 150 | Compact, fast loading |
| Slide deck | 10 | 6 | 150 | Fills a 16:9 slide |
| Journal figure | 7 | 5 | 300 | Typical single-column width |
| Poster panel | 12 | 8 | 300 | Large format |
| Retina display | 6 | 4 | 200 | Crisp on HiDPI screens |

## Saving from a Variable

Assign the plot to a variable, then call `.save()`. This is the standard
pattern for programmatic workflows.

```python
from plotnine import *
from plotnine.data import mpg

p = (
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(cyl)"))
    + geom_point(alpha=0.6)
    + labs(x="Engine Displacement (L)", y="Highway MPG", color="Cylinders", title="Colored Scatter")
)

# Save multiple formats
p.save("scatter.png", width=6, height=4, dpi=300)
p.save("scatter.pdf", width=6, height=4)
p.save("scatter.svg", width=6, height=4)
```

## In-Memory Saving

Save to a `BytesIO` buffer for web apps, APIs, or notebook display without
writing to disk.

```python
from io import BytesIO
from plotnine import *
from plotnine.data import mpg

p = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="In-Memory Plot")
)

buf = BytesIO()
p.save(buf, format="png", width=6, height=4, dpi=150)
buf.seek(0)
# buf.getvalue() contains the PNG bytes
```

## Retina / HiDPI

For retina displays, use `dpi=200` or higher. The plot dimensions stay the
same, but the pixel count doubles, producing crisp text and lines.

```python
from plotnine import *
from plotnine.data import mpg

p = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Retina Plot")
)

p.save("retina_plot.png", width=6, height=4, dpi=200)
```

## Common Pitfalls

- **Forgetting `width` and `height`**: Without explicit dimensions, plotnine
  uses the theme's `figure_size` default (typically 6.4 x 4.8 inches). Always
  specify dimensions for consistent output across environments.

- **Wrong `units`**: The default is `"in"` (inches). If you pass
  `width=15, height=10` without `units="cm"`, the figure will be 15x10 inches
  — very large. Set `units="cm"` or `"mm"` for metric sizes.

- **File extension determines format**: `p.save("plot.pdf")` saves as PDF.
  If you use a non-standard extension, set `format` explicitly:
  `p.save("plot.img", format="png")`.

- **PDF text not selectable**: If text appears as paths in PDF output, ensure
  you are not using unusual fonts. Standard fonts (DejaVu Sans, serif) produce
  selectable text.

## See Also

- [themes-and-styling.md](themes-and-styling.md) — `figure_size` as
  the in-theme alternative to `save(width, height)`
- [composition.md](composition.md) — saving composed plots has
  different size semantics (no `width`/`height` on `.save()`)
