# scale_color_manual

Custom discrete color scale

## Signature

`scale_color_manual( values, *, name=None, breaks=True, limits=None, labels=True, expand=None, guide="legend", na_value="#7F7F7F", aesthetics=(), drop=True, na_translate=True )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `values` | Sequence[Any] \| dict[Any, Any] |  | Colors that make up the palette. The values will be matched with the limits of the scale or the breaks if provided. If it is a dict then it should map data values to colors. |
| `name` | str \| None | `None` | The name of the scale. It is used as the label of the axis or the title of the guide. Suitable defaults are chosen depending on the type of scale. |
| `breaks` | DiscreteBreaksUser | `True` | List of major break points. Or a callable that takes a tuple of limits and returns a list of breaks. If True, automatically calculate the breaks. |
| `limits` | DiscreteLimitsUser | `None` | Limits of the scale. These are the categories (unique values) of the variables. If is only a subset of the values, those that are left out will be treated as missing data and represented with a na_value. |
| `labels` | ScaleLabelsUser | `True` | Labels at the breaks. Alternatively, a callable that takes an array_like of break points as input and returns a list of strings. |
| `expand` | ( tuple[float, float] \| tuple[float, float, float, float] \| None) | `None` | Multiplicative and additive expansion constants that determine how the scale is expanded. If specified must be of length 2 or 4. Specifically the values are in this order: For example, If not specified, suitable defaults are chosen. |
| `guide` | Literal["legend"] \| None | `"legend"` |  |
| `na_value` | str | `"#7F7F7F"` |  |
| `aesthetics` | Sequence[ScaledAestheticsName] | `()` | Aesthetics affected by this scale. These are defined by each scale and the user should probably not change them. Have fun. |
| `drop` | bool | `True` | Whether to drop unused categories from the scale |
| `na_translate` | bool | `True` | If True translate missing values and show them. If False remove missing values. |

## Examples

### Assign specific colors per level

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species"))
    + geom_point()
    + scale_color_manual(values=["#E69F00", "#56B4E9", "#009E73"])
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguins (Manual Colors)", color="Species")
)
```
