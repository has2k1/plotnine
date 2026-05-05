# scale_color_datetime

Datetime color scale

## Signature

`scale_color_datetime( cmap_name="viridis", date_breaks=None, date_labels=None, date_minor_breaks=None, *, name=None, breaks=True, limits=None, labels=True, expand=None, guide="colorbar", na_value="#7F7F7F", aesthetics=(), rescaler=rescale, oob=censor, minor_breaks=True, trans="datetime" )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `cmap_name` | str | `'viridis'` | A standard Matplotlib colormap name. The default is viridis. For the list of names checkout the output of matplotlib.cm.cmap_d.keys() or see colormaps. |
| `date_breaks` | str \| None | `None` | A string giving the distance between major breaks. For example '2 weeks', '5 years'. If specified, date_breaks takes precedence over breaks. |
| `date_labels` | str \| None | `None` | Format string for the labels. See strftime. If specified, date_labels takes precedence over labels. |
| `date_minor_breaks` | str \| None | `None` | A string giving the distance between minor breaks. For example '2 weeks', '5 years'. If specified, date_minor_breaks takes precedence over minor_breaks. |
| `name` | str \| None | `None` | The name of the scale. It is used as the label of the axis or the title of the guide. Suitable defaults are chosen depending on the type of scale. |
| `breaks` | ContinuousBreaksUser | `True` | Major breaks |
| `limits` | ContinuousLimitsUser | `None` | Limits of the scale. Most commonly, these are the minimum & maximum values for the scale. If not specified they are derived from the data. It may also be a function that takes the derived limits and transforms them into the final limits. |
| `labels` | ScaleLabelsUser | `True` | Labels at the breaks. Alternatively, a callable that takes an array_like of break points as input and returns a list of strings. |
| `expand` | ( # pyright: ignore[reportIncompatibleVariableOverride] tuple[float, timedelta] \| tuple[float, timedelta, float, timedelta] \| None) | `None` | Multiplicative and additive expansion constants that determine how the scale is expanded. If specified must be of length 2 or 4. Specifically the values are in this order: For example, If not specified, suitable defaults are chosen. |
| `guide` | Literal["legend", "colorbar"] \| None | `"colorbar"` |  |
| `na_value` | str | `"#7F7F7F"` | Color of missing values. |
| `aesthetics` | Sequence[ScaledAestheticsName] | `()` | Aesthetics affected by this scale. These are defined by each scale and the user should probably not change them. Have fun. |
| `rescaler` | PRescale | `rescale` | Function to rescale data points so that they can be handled by the palette. Default is to rescale them onto the [0, 1] range. Scales that inherit from this class may have another default. |
| `oob` | PCensor | `censor` | Function to deal with out of bounds (limits) data points. Default is to turn them into np.nan, which then get dropped. |
| `minor_breaks` | MinorBreaksUser | `True` | If a list-like, it is the minor breaks points. If an integer, it is the number of minor breaks between any set of major breaks. If a function, it should have the signature func(limits) and return a list-like of consisting of the minor break points. If None, no minor breaks are calculated. The default is to automatically calculate them. |
| `trans` | TransUser | `"datetime"` |  |
