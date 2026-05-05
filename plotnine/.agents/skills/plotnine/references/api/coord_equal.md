# coord_equal

Cartesian coordinates with fixed relationship between x and y scales

## Signature

`coord_equal(ratio=1, xlim=None, ylim=None, expand=True)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `ratio` | float | `1` | Desired aspect_ratio (:math:y/x) of the panel(s). |
| `xlim` | tuple[float, float] | `None` | Limits for x axis. If None, then they are automatically computed. |
| `ylim` | tuple[float, float] | `None` | Limits for y axis. If None, then they are automatically computed. |
| `expand` | bool | `True` | If True, expand the coordinate axes by some factor. If False, use the limits from the data. |
