# stat_ellipse

Calculate normal confidence interval ellipse

## Signature

`stat_ellipse( mapping=None, data=None, *, geom="path", position="identity", na_rm=False, type="t", level=0.95, segments=51, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"path"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `type` | Literal["t", "norm", "euclid"] | `"t"` | The type of ellipse. t assumes a multivariate t-distribution. norm assumes a multivariate normal distribution. euclid draws a circle with the radius equal to level, representing the euclidean distance from the center. |
| `level` | float | `0.95` | The confidence level at which to draw the ellipse. |
| `segments` | int | `51` | Number of segments to be used in drawing the ellipse. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
