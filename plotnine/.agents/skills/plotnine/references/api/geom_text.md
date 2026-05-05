# geom_text

Textual annotations

## Signature

`geom_text( mapping=None, data=None, *, stat="identity", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, parse=False, nudge_x=0, nudge_y=0, adjust_text=None, format_string=None, path_effects=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Aesthetics Descriptions Float or one of: Horizontal alignment. One of {"left", "center", "right"}. Vertical alignment. One of {"top", "center", "bottom", "baseline", "center_baseline"}. Font family. Can be a font name e.g. “Arial”, “Helvetica”, “Times”, … or a family that is one of {"serif", "sans-serif", "cursive", "fantasy", "monospace"}} Font weight. A numeric value in range 0-1000 or a string that is one of: Font style. One of {"normal", "italic", "oblique"}. Font variant. One of {"normal", "small-caps"}. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"identity"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `parse` | bool | `False` | If True, the labels will be rendered with latex. |
| `nudge_x` | float | `0` | Horizontal adjustment to apply to the text |
| `nudge_y` | float | `0` | Vertical adjustment to apply to the text |
| `adjust_text` |  |  | Parameters to adjust_text will repel overlapping texts. This parameter takes priority of over nudge_x and nudge_y. adjust_text does not work well when it is used in the first layer of the plot, or if it is the only layer. For more see the documentation at. |
| `format_string` | str | `None` | If not None, then the text is formatted with this string using str.format e.g: |
| `path_effects` | list | `None` | If not None, then the text will use these effects. See documentation for more details. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| label |  |
| x |  |
| y |  |
| alpha | 1 |
| angle | 0 |
| color | 'black' |
| family | None |
| fontstyle | 'normal' |
| fontvariant | None |
| fontweight | 'normal' |
| group |  |
| ha | 'center' |
| lineheight | 1.2 |
| size | 11 |
| va | 'center' |
