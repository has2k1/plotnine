# coord_cartesian

Cartesian coordinate system

## Signature

`coord_cartesian(xlim=None, ylim=None, expand=True)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `xlim` | tuple[Any, Any] \| None | `None` | Limits (in data type of the x-aesthetic) for x axis. If None, then they are automatically computed. |
| `ylim` | tuple[Any, Any] \| None | `None` | Limits (in data type of the x-aesthetic) for y axis. If None, then they are automatically computed. |
| `expand` | bool | `True` | If True, expand the coordinate axes by some factor. If False, use the limits from the data. |

## Examples

Zooms into a region without removing data points. Contrast with
`lims()` and `scale_*_continuous(limits=...)`, which **drop** rows
outside the range and therefore affect stats like `geom_smooth`. See
[coords-and-axes.md](../coords-and-axes.md) for the contrast in full.

### Zooming without data removal

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + coord_cartesian(xlim=(2, 5), ylim=(15, 40))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Zoomed View (Data Preserved)")
)
```
