# scale_fill_ordinal

alias of scale_fill_cmap_d

## Signature

`scale_fill_ordinal( cmap_name="viridis", *, name=None, breaks=True, limits=None, labels=True, expand=None, guide="legend", na_value="#7F7F7F", aesthetics=(), drop=True, na_translate=True )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `cmap_name` | str | `'viridis'` | A standard Matplotlib colormap name. The default is viridis. For the list of names checkout the output of matplotlib.cm.cmap_d.keys() or see the documentation. |
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
