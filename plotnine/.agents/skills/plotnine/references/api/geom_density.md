# geom_density

Smooth density estimate

## Signature

`geom_density( mapping=None, data=None, *, stat="density", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, outline_type="upper", **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Aesthetics Descriptions Define where to exclude horizontal regions from being filled. Regions between any two False values are skipped. For sensible demarcation the value used in the where predicate expression should match the ymin value or expression. i.e. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"density"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| alpha | 1 |
| color | 'black' |
| fill | None |
| group |  |
| linetype | 'solid' |
| size | 0.5 |
| weight | 1 |
| where | True |

## Examples

### Density curve

```python
from plotnine import *
from plotnine.data import faithful

(
    ggplot(faithful, aes(x="eruptions"))
    + geom_density()
    + labs(x="Eruption Duration (min)", y="Density", title="Old Faithful Eruption Durations")
)
```
