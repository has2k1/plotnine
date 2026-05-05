# scale_color_gradient

Create a 2 point color gradient

## Signature

`scale_color_gradient( low="#132B43", high="#56B1F7", *, name=None, breaks=True, limits=None, labels=True, expand=None, guide="colorbar", na_value="#7F7F7F", aesthetics=(), rescaler=rescale, oob=censor, minor_breaks=True, trans=None )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `low` | str | `'#132B43'` | Low color. |
| `high` | str | `'#56B1F7'` | High color. |
| `name` | str \| None | `None` | The name of the scale. It is used as the label of the axis or the title of the guide. Suitable defaults are chosen depending on the type of scale. |
| `breaks` | ContinuousBreaksUser | `True` | Major breaks |
| `limits` | ContinuousLimitsUser | `None` | Limits of the scale. Most commonly, these are the minimum & maximum values for the scale. If not specified they are derived from the data. It may also be a function that takes the derived limits and transforms them into the final limits. |
| `labels` | ScaleLabelsUser | `True` | Labels at the breaks. Alternatively, a callable that takes an array_like of break points as input and returns a list of strings. |
| `expand` | ( tuple[float, float] \| tuple[float, float, float, float] \| None) | `None` | Multiplicative and additive expansion constants that determine how the scale is expanded. If specified must be of length 2 or 4. Specifically the values are in this order: For example, If not specified, suitable defaults are chosen. |
| `guide` | Literal["legend", "colorbar"] \| None | `"colorbar"` |  |
| `na_value` | str | `"#7F7F7F"` | Color of missing values. |
| `aesthetics` | Sequence[ScaledAestheticsName] | `()` | Aesthetics affected by this scale. These are defined by each scale and the user should probably not change them. Have fun. |
| `rescaler` | PRescale | `rescale` | Function to rescale data points so that they can be handled by the palette. Default is to rescale them onto the [0, 1] range. Scales that inherit from this class may have another default. |
| `oob` | PCensor | `censor` | Function to deal with out of bounds (limits) data points. Default is to turn them into np.nan, which then get dropped. |
| `minor_breaks` | MinorBreaksUser | `True` | If a list-like, it is the minor breaks points. If an integer, it is the number of minor breaks between any set of major breaks. If a function, it should have the signature func(limits) and return a list-like of consisting of the minor break points. If None, no minor breaks are calculated. The default is to automatically calculate them. |
| `trans` | TransUser | `None` | The transformation of the scale. Either name of a trans function or a trans function. See mizani.transforms for possible options. |

## Examples

### Two-point gradient

```python
from plotnine import *
from plotnine.data import economics

(
    ggplot(economics, aes(x="date", y="unemploy", color="uempmed"))
    + geom_point(size=0.5)
    + scale_color_gradient(low="blue", high="red")
    + labs(x="Date", y="Unemployed (thousands)", title="Unemployment Colored by Duration", color="Median\nDuration (wk)")
)
```
