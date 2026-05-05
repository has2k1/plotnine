# geom_label

Textual annotations with a background

## Signature

`geom_label( mapping=None, data=None, *, stat="identity", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, parse=False, nudge_x=0, nudge_y=0, adjust_text=None, format_string=None, path_effects=None, boxstyle="round", boxcolor=None, label_padding=0.25, label_r=0.25, label_size=0.7, tooth_size=None, **kwargs )`

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
| `boxstyle` | str | `"round"` | Options are: |
| `boxcolor` |  |  | Color of box around the text. If None, the color is the same as the text. |
| `label_padding` | float | `0.25` | Amount of padding |
| `label_r` | float | `0.25` | Rounding radius of corners. |
| `label_size` | float | `0.7` | Linewidth of the label boundary. |
| `tooth_size` | float | `None` | Size of the roundtooth or sawtooth if they are the chosen boxstyle. The default depends on Matplotlib |
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
| fill | 'white' |
| fontstyle | 'normal' |
| fontvariant | None |
| fontweight | 'normal' |
| group |  |
| ha | 'center' |
| lineheight | 1.2 |
| size | 11 |
| va | 'center' |
