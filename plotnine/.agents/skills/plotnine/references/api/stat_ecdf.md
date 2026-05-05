# stat_ecdf

Empirical Cumulative Density Function

## Signature

`stat_ecdf( mapping=None, data=None, *, geom="step", position="identity", na_rm=False, n=None, pad=True, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"step"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `n` |  |  | This is the number of points to interpolate with. If None, do not interpolate. |
| `pad` | bool | `True` | If True, pad the domain with -inf and +inf so that ECDF does not have discontinuities at the extremes. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y | after_stat('ecdf') |

## Examples

### Basic ECDF

```python
from plotnine import *
from plotnine.data import faithful

(
    ggplot(faithful, aes(x="eruptions"))
    + stat_ecdf()
    + labs(x="Eruption Duration (min)", y="Cumulative Proportion", title="ECDF of Old Faithful Eruptions")
)
```

### Grouped ECDF

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="body_mass_g", color="species"))
    + stat_ecdf()
    + labs(x="Body Mass (g)", y="Cumulative Proportion", color="Species", title="Body Mass ECDF by Species")
)
```
