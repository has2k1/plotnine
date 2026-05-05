# geom_raster

Rasterized Rectangles specified using center points

## Signature

`geom_raster( mapping=None, data=None, *, stat="identity", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=True, vjust=0.5, hjust=0.5, interpolation=None, filterrad=4.0, **kwargs )`

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
| `raster` | bool | `True` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `hjust` | float | `0.5` | Horizontal justification for the rectangle at point x. Default is 0.5, which centers the rectangle horizontally. Must be in the range [0, 1]. |
| `vjust` | float | `0.5` | Vertical justification for the rectangle at point y Default is 0.5, which centers the rectangle vertically. Must be in the range [0, 1]. |
| `interpolation` | str | `None` | How to calculate values between the center points of adjacent rectangles. The default is None not to interpolate. Allowed values are: |
| `filterrad` | float | `4.0` | The filter radius for filters that have a radius parameter, i.e. when interpolation is one of: sinc, lanczos, blackman. Must be a number greater than zero. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| alpha | 1 |
| fill | '#333333' |
| group |  |
