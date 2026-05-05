# geom_rug

Marginal rug plot

## Signature

`geom_rug( mapping=None, data=None, *, stat="identity", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, sides="bl", length=0.03, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"identity"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `sides` | str | `"bl"` | Sides onto which to draw the marks. Any combination chosen from the characters "btlr", for bottom, top, left or right side marks. |
| `length` |  |  | length of marks in fractions of horizontal/vertical panel size. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| alpha | 1 |
| color | 'black' |
| group |  |
| linetype | 'solid' |
| size | 0.5 |

## Examples

### Rug plot on a scatter

`geom_rug` draws tick marks along axes to show individual data values.
The `sides` parameter controls which axes get rugs: `"b"` (bottom),
`"l"` (left), `"t"` (top), `"r"` (right), or any combination like
`"bl"`.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + geom_rug(sides="bl", length=0.03, alpha=0.3)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Scatter with Marginal Rugs")
)
```
