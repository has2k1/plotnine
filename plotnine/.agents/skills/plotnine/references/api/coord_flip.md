# coord_flip

Flipped cartesian coordinates

## Signature

`coord_flip(xlim=None, ylim=None, expand=True)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `xlim` | tuple[float, float] | `None` | Limits for x axis. If None, then they are automatically computed. |
| `ylim` | tuple[float, float] | `None` | Limits for y axis. If None, then they are automatically computed. |
| `expand` | bool | `True` | If True, expand the coordinate axes by some factor. If False, use the limits from the data. |

## Examples

Swaps the x and y axes. Useful for horizontal bar charts and
horizontal box plots. Aesthetic mapping stays the same — define the
category on `x=` even when it ends up drawn on the vertical axis.

### Horizontal bar chart

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class"))
    + geom_bar()
    + coord_flip()
    + labs(x="Vehicle Class", y="Count", title="Horizontal Bar Chart")
)
```

### Horizontal box plot

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="cut", y="price"))
    + geom_boxplot()
    + coord_flip()
    + labs(x="Cut", y="Price (USD)", title="Diamond Price by Cut (Horizontal)")
)
```
