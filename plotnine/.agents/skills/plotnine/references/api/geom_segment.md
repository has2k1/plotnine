# geom_segment

Line segments

## Signature

`geom_segment( mapping=None, data=None, *, stat="identity", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, lineend="butt", arrow=None, **kwargs )`

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
| `lineend` | Literal["butt", "round", "projecting"] | `"butt"` | Line end style. This option is applied for solid linetypes. |
| `arrow` | arrow | `None` | Arrow specification. Default is no arrow. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| xend |  |
| y |  |
| yend |  |
| alpha | 1 |
| color | 'black' |
| group |  |
| linetype | 'solid' |
| size | 0.5 |

## Examples

### Segments with arrowheads

The `arrow()` helper creates arrowheads with parameters:

| Parameter | Default  | Description                                             |
|-----------|----------|---------------------------------------------------------|
| `angle`   | `30`     | Angle in degrees between tail and edge                  |
| `length`  | `0.2`    | Length of the arrowhead edge in inches                  |
| `ends`    | `"last"` | Draw arrowhead at `"first"`, `"last"`, or `"both"` ends |
| `type`    | `"open"` | `"open"` or `"closed"` (closed is also filled)          |

```python
from plotnine import *
import pandas as pd

df = pd.DataFrame({
    "x": [1, 3, 5],
    "y": [1, 3, 2],
    "xend": [2, 4, 6],
    "yend": [3, 1, 4],
})

(
    ggplot(df, aes(x="x", y="y", xend="xend", yend="yend"))
    + geom_segment(arrow=arrow(angle=25, length=0.15, type="closed"))
    + labs(x="X", y="Y", title="Directed Arrows")
)
```
