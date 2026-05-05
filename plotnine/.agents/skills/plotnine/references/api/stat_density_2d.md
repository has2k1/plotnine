# stat_density_2d

Compute 2D kernel density estimation

## Signature

`stat_density_2d(mapping=None, data=None, **kwargs)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `contour` | bool | `True` | Whether to create contours of the 2d density estimate. |
| `n` | int | `64` | Number of equally spaced points at which the density is to be estimated. For efficient computation, it should be a power of two. |
| `levels` | int \| array_like | `5` | Contour levels. If an integer, it specifies the maximum number of levels, if array_like it is the levels themselves. |
| `package` | Literal["statsmodels", "scipy", "sklearn"] | `"statsmodels"` | Package whose kernel density estimation to use. |
| `kde_params` | dict |  | Keyword arguments to pass on to the kde class. |
