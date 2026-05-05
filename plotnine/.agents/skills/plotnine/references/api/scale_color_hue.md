# scale_color_hue

Qualitative color scale with evenly spaced hues

## Signature

`scale_color_hue( h=15, c=100, l=65, direction=1, *, name=None, breaks=True, limits=None, labels=True, expand=None, guide="legend", na_value="#7F7F7F", aesthetics=(), drop=True, na_translate=True )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `h` | float \| tuple[float, float] | `15` | Hue. If a float, it is the first hue value, in the range [0, 360]. The range of the palette will be [first, first + 360). If a tuple, it is the range [first, last) of the hues. |
| `c` | float | `100` | Chroma. Must be in the range [0, 100] |
| `l` | float | `65` | Lightness. Must be in the range [0, 100] |
| `direction` | Literal[1, -1] | `1` | The order of colours in the scale. If -1 the order of colours is reversed. The default is 1. |
| `name` | str \| None | `None` | The name of the scale. It is used as the label of the axis or the title of the guide. Suitable defaults are chosen depending on the type of scale. |
| `breaks` | DiscreteBreaksUser | `True` | List of major break points. Or a callable that takes a tuple of limits and returns a list of breaks. If True, automatically calculate the breaks. |
| `limits` | DiscreteLimitsUser | `None` | Limits of the scale. These are the categories (unique values) of the variables. If is only a subset of the values, those that are left out will be treated as missing data and represented with a na_value. |
| `labels` | ScaleLabelsUser | `True` | Labels at the breaks. Alternatively, a callable that takes an array_like of break points as input and returns a list of strings. |
| `expand` | ( tuple[float, float] \| tuple[float, float, float, float] \| None) | `None` | Multiplicative and additive expansion constants that determine how the scale is expanded. If specified must be of length 2 or 4. Specifically the values are in this order: For example, If not specified, suitable defaults are chosen. |
| `guide` | Literal["legend"] \| None | `"legend"` |  |
| `na_value` | str | `"#7F7F7F"` | Color of missing values. |
| `aesthetics` | Sequence[ScaledAestheticsName] | `()` | Aesthetics affected by this scale. These are defined by each scale and the user should probably not change them. Have fun. |
| `drop` | bool | `True` | Whether to drop unused categories from the scale |
| `na_translate` | bool | `True` | If True translate missing values and show them. If False remove missing values. |
