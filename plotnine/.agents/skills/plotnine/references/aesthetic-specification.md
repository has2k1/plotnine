# Aesthetic Specification

How to *literally* specify values for aesthetic properties like color,
linetype, point shape, size, and text. This is the concrete-values
reference — for mapping data variables to aesthetics, see
[aesthetics-and-scales.md](aesthetics-and-scales.md).

Use these forms outside `aes()` (fixed values, no legend) or as the
`values=` argument to `scale_*_manual()`.

## Color and Fill

Color accepts:

- **Named colors** — any matplotlib-recognized name: `"red"`,
  `"steelblue"`, `"navy"`, `"forestgreen"`.
- **Hex codes** — `"#RRGGBB"` or `"#RRGGBBAA"` (alpha in the last pair).
- **`"none"`** — fully transparent (for fill or border).

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(color="#E69F00", size=2, alpha=0.7)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fixed color and alpha")
)
```

For a transparent fill with a visible border use `fill="none"` and set
`color` explicitly.

## Linetype

Named types: `"solid"`, `"dashed"`, `"dotted"`, `"dashdot"`, plus
`"longdash"` and `"twodash"`.

Custom dash patterns are `(offset, (on, off, on, off, ...))` tuples in
point units. The second element repeats the on/off pattern indefinitely.

```python
from plotnine import *
import pandas as pd

df = pd.DataFrame({
    "x": list(range(10)) * 3,
    "y": list(range(10)) + [v + 1 for v in range(10)] + [v + 2 for v in range(10)],
    "series": ["a"] * 10 + ["b"] * 10 + ["c"] * 10,
})

(
    ggplot(df, aes(x="x", y="y", group="series"))
    + geom_line(linetype="dashed", size=0.8)
    + labs(x="X", y="Y", title="Dashed line with fixed linetype")
)
```

## Line Attributes

- **`size`** — line thickness, in approximately 0.75 mm units.
- **`lineend`** — `"round"`, `"butt"`, or `"square"`. Controls the shape
  of the end of an un-joined line.
- **`linejoin`** — `"round"`, `"mitre"`, or `"bevel"`. Controls corners
  where line segments meet.

```python
from plotnine import *
import pandas as pd

df = pd.DataFrame({"x": [0, 1, 2, 3], "y": [0, 2, 1, 3]})

(
    ggplot(df, aes(x="x", y="y"))
    + geom_line(size=2, lineend="round", linejoin="bevel", color="#009E73")
    + labs(x="X", y="Y", title="Thick line with rounded ends and beveled joins")
)
```

## Point Shape

Shape accepts:

- **Integers** (0–25) — standard matplotlib marker codes. Selected
  common values:

| Integer | Shape                   |
|---------|-------------------------|
| 0       | open square             |
| 1       | open circle             |
| 2       | open triangle up        |
| 3       | plus                    |
| 4       | cross (×)               |
| 15      | filled square           |
| 16      | filled circle (default) |
| 17      | filled triangle         |
| 19      | large filled circle     |

- **Single-character strings** — `"+"`, `"x"`, `"*"`, `"."`.
- **Mathtex strings** — `r"$\alpha$"`, `r"$\heartsuit$"`.
- **Polygon tuples** — `(n_sides, style, rotation)` where style is
  `0` (regular polygon), `1` (star), or `2` (asterisk).

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(shape="D", size=3, color="#56B4E9")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Points with fixed shape 'D'")
)
```

## Point Sizing

- **`size`** — diameter in mm. Default is about 1.5.
- **`stroke`** — outline width in mm (applies to open shapes only).

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(shape="o", size=4, stroke=0.8, color="#D55E00")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Open circles with thick stroke")
)
```

## Text

Applies to `geom_text`, `geom_label`, and `theme(text=element_text(...))`.

- **`family`** — generic families (`"sans"`, `"serif"`, `"mono"`) or a
  specific installed font name (`"Arial"`, `"DejaVu Sans"`).
- **`weight`** — `"normal"`, `"bold"`, `"light"`, `"heavy"`, or numeric
  (100–900).
- **`style`** — `"normal"`, `"italic"`, `"oblique"`.
- **`size`** — in mm by default for `geom_text` / `geom_label`; in
  points within `theme()` elements.
- **`ha`** / **`va`** — horizontal and vertical alignment. Strings
  (`"left"`, `"center"`, `"right"`; `"top"`, `"center"`, `"bottom"`) or
  floats in the 0–1 range.
- **`color`** — any color accepted above.

```python
from plotnine import *
import pandas as pd

df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "label": ["A", "B", "C"]})

(
    ggplot(df, aes(x="x", y="y", label="label"))
    + geom_text(family="serif", style="italic", weight="bold", size=14, color="#0072B2")
    + labs(x="X", y="Y", title="Styled text labels")
)
```

## Common Pitfalls

- **Color inside vs outside `aes()`**: `aes(color="red")` creates a
  legend entry for the literal string `"red"`. To set a fixed color,
  put it outside `aes()`: `geom_point(color="red")`.

- **`size` units differ by context**: for `geom_point`/`geom_text`,
  size is in mm. Inside `theme(text=element_text(size=...))`, size is
  in points. A 12 pt font is roughly 4.2 mm.

- **Linetype tuple form**: the outer tuple is `(offset, pattern)`, not
  a flat list. `(0, (4, 4))` is valid; `(4, 4)` alone is not.

- **Shape integers don't all accept `fill`**: open shapes (0–14) use
  only `color` and `stroke`. Filled shapes (15–25) use `fill` for the
  interior and `color` for the border.

## See Also

- [aesthetics-and-scales.md](aesthetics-and-scales.md) — mapping
  variables to aesthetics, scale customization
- [themes-and-styling.md](themes-and-styling.md) — theme elements and
  the `theme()` surface
