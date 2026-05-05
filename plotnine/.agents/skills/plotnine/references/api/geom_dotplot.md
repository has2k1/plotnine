# geom_dotplot

Dot plot

## Signature

`geom_dotplot( mapping=None, data=None, *, stat="bindot", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, stackdir="up", stackratio=1, dotsize=1, stackgroups=False, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"bindot"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `stackdir` | Literal["up", "down", "center", "centerwhole"] | `"up"` | Direction in which to stack the dots. Options are |
| `stackratio` | float | `1` | How close to stack the dots. If value is less than 1, the dots overlap, if greater than 1 they are spaced. |
| `dotsize` | float | `1` | Diameter of dots relative to binwidth. |
| `stackgroups` | bool | `False` | If True, the dots are stacked across groups. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| alpha | 1 |
| color | 'black' |
| fill | 'black' |
| group |  |
